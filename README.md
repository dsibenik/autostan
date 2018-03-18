# autostan
A node program to scrape njuskalo.hr, index.hr/oglasi and oglasnik.hr for new entries.

## Requirements
[nodejs](https://nodejs.org/en/)

## Installation
1. Clone the node-dev branch of the repository:
	```
	git clone -b node-dev https://github.com/dsibenik/autostan
	```

2. Configure parameters in config.json:
	- **from** - gmail address which sends notifications
	- **to** - email address which receives notifications (can be the same as gmail)
	- **subject** -  subject line of the notifications
	- **njuskalo**, **oglasnik**, **index** - links to respective sites with filters applied

	Note: you might have to allow the app use the gmail account, instructions [here](https://support.google.com/accounts/answer/6010255?hl=en).

3. Install node_modules:
	```
	npm install
	```

4. Start program:
	```
	npm start
	```