import discord
import math
import random
from typing import Callable, Optional, Any
from datetime import timedelta
import requests

def random_hex():
    return random.randint(0, 0xFFFFFF)

async def poll_ics_once(client, users, *, now, canvas_utils, log, image_links):
    for uid_str, cfg in list(users.items()):
        try:
            uid = int(uid_str)
        except ValueError:
            continue

        ics_url = (cfg or {}).get("ics_link")
        if not ics_url:
            continue

        localtz = canvas_utils.tz_for_user(uid=uid)
        end = now + timedelta(days=canvas_utils.LOOKAHEAD_DAYS)

        try:
            r = requests.get(ics_url, timeout=30)
            r.raise_for_status()
            cal = canvas_utils.parse_ics(r.content)
        except Exception as e:
            log.error(f"[{uid}] ICS fetch error: {e}")
            continue

        reminded = canvas_utils.load_reminded(uid=uid) or {}
        changed = False

        for comp in cal.walk():
            if getattr(comp, "name", None) != "VEVENT":
                continue

            start = canvas_utils.event_start(comp=comp, localtz=localtz)
            if not start or start <= now or start > end:
                continue

            title = str(comp.get("SUMMARY") or "No summary given").strip()
            url = canvas_utils.event_url(comp=comp)
            desc = canvas_utils.event_description(comp=comp)
            if not canvas_utils.looks_like_assignment(title, desc, url):
                continue

            event_id = canvas_utils.event_uid(comp=comp, start_iso=start.isoformat())
            fp = canvas_utils.event_fingerprint(comp=comp, localtz=localtz)
            old_fp = reminded.get(event_id)

            if old_fp and old_fp != fp:
                # send "updated" DM (your embed construction here)
                try:
                    user = await client.fetch_user(uid)
                    await user.send(f"⏰ Due date updated: {title}")
                except discord.Forbidden as e:
                    log.error(f"DM blocked for {uid}: {e}")
                reminded[event_id] = fp
                changed = True

            if reminded.get(event_id) == fp:
                continue

            if canvas_utils.remind_alert(now, start):
                # send 24h reminder (your embed construction here)
                try:
                    user = await client.fetch_user(uid)
                    await user.send(f"🍂 {title} is due in ~1 day")
                except discord.Forbidden as e:
                    log.error(f"DM blocked for {uid}: {e}")
                reminded[event_id] = fp
                changed = True

        if changed:
            canvas_utils.save_reminded(uid=uid, state=reminded)


class EmbedPaginator(discord.ui.View):
    def __init__(
        self,
        items: list[Any],
        *,
        author_id: int,
        per_page: int = 10,
        color: int | discord.Color,
        embed_title: str,
        page_desc: Optional[Callable[[int, int, int, int], str]] = None,
        render_item: Callable[[discord.Embed, Any], None],
        thumb_url: Optional[str] = None,
        footer_text: Optional[str] = None,
        timeout: float = 120.0,
    ):
        super().__init__(timeout=timeout)
        self.items = items
        self.author_id = author_id
        self.per_page = max(1, per_page)
        self.page = 0
        self.color = color
        self.embed_title = embed_title
        self.page_desc_cb = page_desc
        self.render_item = render_item
        self.thumb_url = thumb_url
        self.footer_text = footer_text

        self.total_pages = max(1, math.ceil(len(self.items) / self.per_page))

        if self.total_pages <= 1:
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True

        self._set_button_states()

    def _slice(self):
        start = self.page * self.per_page
        end = start + self.per_page
        return self.items[start:end], start, end

    def _make_embed(self) -> discord.Embed:
        page_items, start, end = self._slice()
        embed = discord.Embed(
            title=self.embed_title,
            color=self.color
        )
        if self.page_desc_cb:
            embed.description = self.page_desc_cb(self.page + 1, self.total_pages, start + 1, min(end, len(self.items)))
        elif self.total_pages > 1:
            embed.description = f"Page {self.page + 1}/{self.total_pages} — showing {start + 1}-{min(end, len(self.items))} of **{len(self.items)}**"

        if self.thumb_url:
            embed.set_thumbnail(url=self.thumb_url)

        for it in page_items:
            self.render_item(embed, it)

        if self.footer_text:
            embed.set_footer(text=self.footer_text)
        elif self.total_pages > 1:
            embed.set_footer(text=f"Use the buttons to navigate • Total items: {len(self.items)}")

        return embed

    def _set_button_states(self):
        first_btn = self.children[0]
        prev_btn = self.children[1]
        next_btn = self.children[2]
        last_btn = self.children[3]
        first_btn.disabled = (self.page == 0)
        prev_btn.disabled = (self.page == 0)
        next_btn.disabled = (self.page >= self.total_pages - 1)
        last_btn.disabled = (self.page >= self.total_pages - 1)

    async def _ensure_author(self, interaction: discord.Interaction | discord.MessageInteraction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the original requester can use these controls.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._ensure_author(interaction): return
        self.page = 0
        self._set_button_states()
        await interaction.response.edit_message(embed=self._make_embed(), view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._ensure_author(interaction): return
        if self.page > 0:
            self.page -= 1
        self._set_button_states()
        await interaction.response.edit_message(embed=self._make_embed(), view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._ensure_author(interaction): return
        if self.page < self.total_pages - 1:
            self.page += 1
        self._set_button_states()
        await interaction.response.edit_message(embed=self._make_embed(), view=self)

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._ensure_author(interaction): return
        self.page = self.total_pages - 1
        self._set_button_states()
        await interaction.response.edit_message(embed=self._make_embed(), view=self)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
