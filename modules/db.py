import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

class SislyDB:
    connection = None
    def __init__(self):
        load_dotenv()  
        pass

    def is_connected(self):
        return self.connection.is_connected()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(host=os.environ.get("MYSQL_HOST"),
                                             database=os.environ.get('MYSQL_DATABASE'),
                                             user=os.environ.get("MYSQL_USER"),
                                             password=os.environ.get("MYSQL_PASSWORD"))
        except Error as e:
            print("Error connecting to database.")

    def count_media_log(self, site=None, url=None):
        if self.is_connected():
            cursor = self.connection.cursor()
            if url == None and site != None:
                sql = "SELECT COUNT(*) FROM `sisly_media_logs` WHERE `site` = %s"
                cursor.execute(sql, (site,))
            elif site == None and url != None:
                sql = "SELECT COUNT(*) FROM `sisly_media_logs` WHERE `url` = %s"
                cursor.execute(sql, (url,))
            elif site != None and url != None:
                sql = "SELECT COUNT(*) FROM `sisly_media_logs` WHERE `site` = %s AND `url` = %s"
                cursor.execute(sql, (site,url))
            else:
                return -1
            (total,) = cursor.fetchone()
            return total
        else:
            return -1

    def insert_media_log(self, site, url):
        if self.is_connected():
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO sisly_media_logs (site, url) VALUES(%s, %s)",(site, url))
            id = cursor.lastrowid
            self.connection.commit()
            return id
        else:
            return None

    def get_queue(self):
        if self.is_connected():
            cursor = self.connection.cursor()
            sql = "SELECT url FROM `sisly_queue`"
            cursor.execute(sql)
            records = cursor.fetchall()
            return records
        else:
            return -1

    def queue_delete(self, url):
        if self.is_connected():
            cursor = self.connection.cursor()
            try:
                cursor.execute("DELETE FROM sisly_queue WHERE url = %s",(url,))
                self.connection.commit()
            except:
                return None
            return True
        else:
            return False
    def queue_url(self, url):
        if self.is_connected():
            cursor = self.connection.cursor()
            try:
                cursor.execute("INSERT INTO sisly_queue (url) VALUES(%s)",(url,))
                id = cursor.lastrowid
                self.connection.commit()
            except:
                return None
            return id
        else:
            return None

    def insert_log(self, url, status):
        if self.is_connected():
            cursor = self.connection.cursor()
            site = urlparse(url).netloc
            cursor.execute("INSERT INTO sisly_logs (site, url, status) VALUES(%s, %s, %s)",(site, url, status))
            id = cursor.lastrowid
            self.connection.commit()
            return id
        else:
            return None

    def update_log(self, id, status=None, current_page=None, total_pages=None, current_link=None, total_links=None, total_images=None, total_videos=None, start_time=None, stop_time=None):
        if self.is_connected():
            cursor = self.connection.cursor()
            d = {}
            if status != None:
                d["status"] = status
            if current_page != None:
                d["dl_current_page"] = current_page
            if total_pages != None:
                d["dl_total_pages"] = total_pages
            if current_link != None:
                d["dl_current_link"] = current_link
            if total_links != None:
                d["dl_total_links"] = total_links
            if total_images != None:
                d["dl_total_images"] = total_images
            if total_videos != None: 
                d["dl_total_videos"] = total_videos
            if start_time != None:
                d["dl_start_time"] = start_time
            if stop_time != None:
                d["dl_stop_time"] = stop_time
            query = 'UPDATE sisly_logs SET {} WHERE id = %s'.format(', '.join('{}=%s'.format(k) for k in d))
            d["id"] = id
            cursor.execute(query, list(d.values()))
            self.connection.commit()

    def disconnect(self):
        if self.is_connected():
            self.connection.close()


if __name__ == "__main__":
    db = SislyDB()
    db.connect()
    id = db.insert_log("SislyDB", "bdsmlr.com/url", "STARTING")
    print(id)
    db.update_log(id, status="FINISHED")
    db.disconnect()