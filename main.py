from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# execute(['scrapy', 'crawl', 'crawler'])
# execute(['scrapy', 'crawl', 'topic_creators'])
execute(['scrapy', 'crawl', 'topicitems'])