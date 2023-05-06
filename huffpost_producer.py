import logging
import typing
import json
from datetime import datetime
import sqlite3
import sys
from ndn import appv2
from ndn import encoding as enc
from ndn.security.keychain.keychain_digest import KeychainDigest

logging.basicConfig(format='[{asctime}]{levelname}:{message}', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO,
                    style='{')

app = appv2.NDNApp()
keychain = KeychainDigest()
signer = keychain.get_signer({})

conn: sqlite3.Connection
cur: sqlite3.Cursor

@app.route('/huffpost/archives')
def on_interest(name: enc.FormalName, _app_param: typing.Optional[enc.BinaryStr],
                reply: appv2.ReplyFunc, context: appv2.PktContext):
    print(f'>> I: {enc.Name.to_str(name)}, {context["int_param"]}')
    content = "Hello, world!".encode()
    reply(app.make_data(name, content=content, signer=signer,
                        freshness_period=10000))
    print(f'<< D: {enc.Name.to_str(name)}')
    print(enc.MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    print('')


def setup_news_table():
    global conn, cur
    try:
        logging.info("Setting up the SQLite Database")
        conn = sqlite3.connect("news_archive.db")
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS news_archive")
        cur.execute("CREATE TABLE news_archive(article_date, link, headline, category, authors, short_description)")
        cur.execute("CREATE INDEX article_date_index ON news_archive(article_date) ")
        # TODO: offer search by author by indexing the author names.
        # cur.execute("CREATE INDEX article_authors_index ON news_archive(authors) ")
        logging.info("Successfully created the table for news_archive in our SQLITE3 Database")
    except Exception:
        logging.error("Encountered Exception while building the database.")
        logging.error(sys.exc_info())
        exit(1)


def read_dataset():
    global conn, cur
    try:
        cur = conn.cursor()
        news_list = []
        logging.info("Reading the news dataset")
        with open('News_Category_Dataset_v3.json', 'r') as news_file:
            logging.info("Reading the file \'News_Category_Dataset_v3.json\'")
            for line in news_file.readlines():
                news_item = json.loads(line)
                news_list.append((datetime.strptime(news_item['date'], '%Y-%m-%d').date(), news_item['link'],
                                  news_item['headline'], news_item['category'], news_item['authors'],
                                  news_item['short_description']))
            cur.executemany("INSERT INTO news_archive VALUES (?, ? , ?, ?, ?, ?)", news_list)
            conn.commit()
            logging.info("Successfully finished reading the news data into the sqlite database!")
    except FileNotFoundError:
        logging.error("Could not find file for the news dataset from kaggle - please download and unzip the file as\n"
                      "\'News_Category_Dataset_v3.json\' in the same directory as this program. available at:\n"
                      "https://www.kaggle.com/datasets/rmisra/news-category-dataset")
        logging.error(sys.exc_info())
        exit(1)
    except sqlite3.OperationalError:
        logging.error("Encountered error while feeding news articles into Sqlite3 DB")
        logging.error(sys.exc_info())
        exit()
    except Exception as err:
        logging.error("Suffered from error - while reading file. Cannot Continue")
        logging.debug(sys.exc_info())
        exit()
    finally:
        news_file.close()
        conn.close()


if __name__ == '__main__':
    setup_news_table()
    read_dataset()
    # app.run_forever()
