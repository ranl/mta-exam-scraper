# mta-exam-scraper
Scrap exam information from MTA website

# Demo
[![asciicast](https://asciinema.org/a/4trul1yd7kruv9hltyz3x5brj.png)](https://asciinema.org/a/4trul1yd7kruv9hltyz3x5brj)

# Requirements
* python >= 2.7 && python < 3.0
* python-dev (if you are running on linux)
* pip
* scrapy == 0.24.4

# Installing python stuff on linux
```
sudo apt-get install python python-dev python-pip
```

# Installing python stuff on Mac (via brew)
```
brew install python
```

# Setup
```
sudo pip install scrapy==0.24.4
git clone https://github.com/ranl/mta-exam-scraper.git
```

# Usage
```
cd mta-exam-scraper

# print all the megamot ids & names
scrapy crawl exam_spider -t jsonlines -o - -a only_list_megama=1 --loglevel=ERROR

# scrap all the exams from MTA and print the items as json to STDOUT
scrapy crawl exam_spider -t jsonlines -o - --loglevel=ERROR

# crawl all the exams in MTA and print debug logs
scrapy crawl exam_spider

# crawl only the megama with id of 50000118 (Computer Science)
scrapy crawl exam_spider -a megama=50000118

# crawl all the exams in MTA and output each Item as a json onliner in the /tmp/data_from_crawler.json file
crawl exam_spider -o /tmp/data_from_crawler.json -t jsonlines

# print more help about the scrapy crawl command
scrapy crawl exam_spider --help
```
