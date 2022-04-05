import sqlite3
from tqdm import tqdm

outputFilePath = "./gesamt.csv"

def unixQuery(date):
    global c, cg_str
    
    # Query with small workarounds for sqlite3
    sql ="""SELECT IFNULL(pn.playernumbers, -1) AS playernumbers, IFNULL(pn.twitchnumbers, -1) AS twitchnumbers
                 , CASE WHEN IFNULL(pn.playernumbers, -1) = -1 OR IFNULL(pn.twitchnumbers, -1) = -1 THEN 0 ELSE 1 END AS numbers_exist
                 , CASE WHEN CAST(strftime('%s', gd.release_date) AS int) <= CAST(""" + str(date) + """ AS int) THEN 1 ELSE 0 END AS released
                 , IFNULL(IFNULL(pr.price, min.minprice), 0) AS price
                 , CASE WHEN CAST(strftime('%s', gd.release_date) AS int) > CAST(""" + str(date) + """ AS int) THEN 0
                        WHEN IFNULL(IFNULL(pr.price, min.minprice), 0) = 0 THEN 1
                        ELSE 0
                   END AS is_free
                 , gd.age, gd.controller_support, gd.mac, gd.linux, gd.metacritic, gd.recommendations, gd.achievements 
                 , gd.reviews_total_positive, gd.reviews_total
                 , """ + cg_str + """
            FROM (SELECT date FROM playernumbers pn GROUP BY date ORDER BY date ASC) dat
            CROSS JOIN game_data gd
            LEFT JOIN playernumbers pn ON gd.id = pn.id AND pn.date = dat.date
            LEFT JOIN categories_and_genres cg ON gd.id = cg.id
            LEFT JOIN (SELECT pn.id AS id, pn.date AS date, pr.price AS price
                       FROM playernumbers pn
                       LEFT JOIN prices pr ON pn.id = pr.id AND CAST(pn.date AS int) > CAST(pr.date AS int) / 1000
                       GROUP BY pn.id, pn.date
                       HAVING pr.date = MAX(pr.date)
                      ) pr ON gd.id = pr.id AND pr.date = dat.date
            LEFT JOIN (SELECT id, price AS minprice
                       FROM prices p
                       GROUP BY p.id
                       HAVING date = MIN(date)
                      ) min ON gd.id = min.id
             WHERE dat.date = """ + str(date) + " ORDER BY gd.id ASC"

    c.execute(sql)
    data = []
    for row in c.fetchall():
        for item in row:
            # To keet the Game_id out
            if (item != game_id):
                data.append(item)
    return data

# Main Part
db = sqlite3.connect("game_data.db")
c = db.cursor()


headers = ["playernumbers", "twitchnumbers", "numbers_exist", "released", "price", "is_free", "age", "controller_support", "mac", "linux", "metacritic", "recommendations", "achievements", "reviews_total_positive", "reviews_total"]
main_headers = len(headers)

# Fetch all categories and genres and prepare them for the query with exceptions
c.execute("PRAGMA table_info(categories_and_genres)")
cats_and_gens = []
for column in c.fetchall()[1:]: #starting at 1 to filter ids
    headers.append(column)
    cats_and_gens.append(column)

cg_str = ""
for cg in cats_and_gens:
    cg_str += "IFNULL(NULLIF(cg." + str(cg[1]) + ", null), -1),"
cg_str = cg_str[:-1]

# Fetch all ids
ids = []
sql = """SELECT id FROM game_data ORDER BY id ASC"""
c.execute(sql)
for id in c.fetchall():
    ids.append(id[0])
    
# Fetch all timestamps from the playernumbers table
sql = """SELECT date FROM playernumbers GROUP BY date ORDER BY date ASC"""
c.execute(sql)
unixs = []
for dates in c.fetchall():
    unixs.append(int(dates[0]))


with open(outputFilePath, "w") as f:
    # Building header
    f.writelines("Unix")
    for game_id in ids:
        for i, column in enumerate(headers):
            if (i < main_headers): # with Prices Playernumbers
                f.writelines("," + str(game_id) + "_" + str(column))
            else:
                f.writelines("," + str(game_id) + "_cat" + str(i - main_headers + 1))

    for j, unix in enumerate(tqdm(unixs, desc="Creating .csv file", ncols=130)):
        # Creating a new line in the csv, beginning with the timestamp
        f.writelines("\n" + str(unix))  

        new_ids = [str(id) for id in ids]
        new_ids_str = ",".join(new_ids)

        data = unixQuery(unix)
                
        for l in range (len(headers) * len(new_ids)):
            item = str(data[l])
            if item.lower() == "null" or item == None or item == "None":
                f.writelines(",-1")
            else:
                f.writelines(","+str(data[l]))
        
print("Done!")

db.commit()
db.close()

                    