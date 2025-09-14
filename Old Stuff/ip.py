import phonenumbers
from phonenumbers import geocoder
from phonenumbers import carrier
k = True
while k:

	user = input('Enter the phonenumber you want to trace with the AREA code\n For example: +91394820103945 or +1432483293 : ')
	ch_nmber = phonenumbers.parse(user, "CH")
	print('Location:')
	print(geocoder.description_for_number(ch_nmber, "en"))
	service_nmber = phonenumbers.parse(user, "RO")
	print(carrier.name_for_number(service_nmber, "en"))

	


	