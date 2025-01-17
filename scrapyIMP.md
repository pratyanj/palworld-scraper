1.Install Scrapy: ```pip install scrapy```

2.Creare a new project -> ```scrapy startproject <PROJECT_NAME>```

```
import scrapy
import re

class paldex(scrapy.Spider):
      name = "paldex"

      def start_requests(self):
          urls = ['{Site_URL}']
          for url in urls:
              yield scrapy.Request(url=url, callback=self.parse)
```
Basic Template for a scrapy spider.

3.Run the spider -> ```scrapy crawl <SPIDER_NAME>```

4.Save the data -> ```scrapy crawl <SPIDER_NAME> -o <FILE_NAME>.json```

likewise for csv,json,xml,etc.```scrapy crawl <SPIDER_NAME> -o ./data/<FILE_NAME>.csv```

5.Scrapy shell -> ```scrapy shell <URL>```
