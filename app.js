'use strict';

const request = require("request-promise");
// const fs      = require('fs');

const cheerio    = require("cheerio");
const randomUA   = require('random-ua');
const config     = require("./config.json");
const nodemailer = require("nodemailer");
const prompt     = require('password-prompt');
const sleep      = require('sleep');


const njuskalo = {
	link: config.njuskalo,
	uri: "www.njuskalo.hr"
};
const oglasnik = {
	link: config.oglasnik,
	uri: "www.oglasnik.hr"
};
const index = {
	link: config.index,
	uri: "www.index.hr"
};

const userAgent = randomUA.generate();

async function getListings(site) {
	let list = [];

	if(site.link) {
		const options = {
						    url: site.link,
						    headers: {
								"Accept-Encoding" : "identity",
								"User-Agent"      : userAgent
						    },
					  	};
		try {
			await request.get(options, function(error, response, html){
			    if(!error){
			        let $ = cheerio.load(html);

			        // fs.writeFile("./response.html", html)

			        if (site.uri == "www.njuskalo.hr")
				        $('li.EntityList-item--Regular .entity-title a').each(function(){
				    		list.push("https://www.njuskalo.hr" + this.attribs.href);
				        });

				    if (site.uri == "www.oglasnik.hr")
				    	$('#ads-list a').each(function(){
				    		list.push(this.attribs.href);
				    	});

				    if (site.uri == "www.index.hr")
				    	$('div.results a.result').each(function(){
				    		list.push(this.attribs.href)
				    	});

			    } else {
			    	console.log(error);
			    };
			});
		}
		catch(error) {
			console.log(error)
		}
	};

	if (list.length == 0)
		console.log("Error fetching", site.uri);

	return list;
}; 


async function main() {
	const password = await prompt('Enter password for ' + config.from + ": ");
	const transporter = nodemailer.createTransport({
		service: 'gmail',
		auth: {
		    user: config.from,
		    pass: password
		}
	});

	console.log("Initializing...");
	let listingsOld = [].concat(await getListings(njuskalo), await getListings(index), await getListings(oglasnik));
	console.log("Listings initialized!");

	let html = 'Program successfully initialized.<br/><br/>Getting results from:';
	html = html + "<br/>" + config.njuskalo + "<br/>" + config.index + "<br/>" + config.oglasnik;

	console.log(html)

	let mailOptions = {
		from: config.from, // sender address
		to: config.to, // list of receivers
		subject: config.subject, // Subject line
		html: html// plain text body
	};

	transporter.sendMail(mailOptions, function (err, info) {
	   if(err){
	     console.log(err);
	     process.exit();
	   }
	});

	let counter = 0;
	while(true) {
		console.log("\nRefreshing @", new Date().toLocaleTimeString());
		const listingsNew = [].concat(await getListings(njuskalo), await getListings(index), await getListings(oglasnik));
		const diff = listingsNew.filter( x => !listingsOld.includes(x));
		console.log(diff)
		console.log(typeof(diff))

		if(diff.length > 0) {
			console.log("New listings: ", diff);

			html = "";
			counter++;
			for( let i = 0; i < diff.length; i++)
				html = html + "<br/>" + diff[i];

			mailOptions.subject = config.subject + " " + counter;
			mailOptions.html = html;

			transporter.sendMail(mailOptions, function (err, info) {
			   if(err)
			     console.log(err);
			});

			listingsOld = listingsNew;
		}
		else {
			console.log("No new listings.");
		}
		sleep.sleep(5*60);
	};
};

main();