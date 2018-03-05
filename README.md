# autostan
A Python program to scrape njuskalo.hr, index.hr/oglasi and oglasnik.hr for new entries.

## Requirements
git, python3, pip

## Installation
1. Clone the repository:
	```
	git clone https://github.com/dsibenik/autostan
	```

2. Configure parameters in config.json:
	- **gmail_username**: sends notifications
	- **mail_to**: receives notifications (can be the same as gmail)
	- **njuskalo**, **oglasnik**, **index**: links to respective sites with filters applied

	Note: you might have to let the app use the account, instructions [here](https://support.google.com/accounts/answer/6010255?hl=en).

3. Install requirements:
	```
	pip3 install bs4 selenium xvfbwrapper
	```

4. Start program:
	```
	python3 autostan.py
	```