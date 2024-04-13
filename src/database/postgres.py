import os
import psycopg

class Database:

    def __init__(self):
        conninfo = os.getenv("LOTTO_DATABASE")
        if not conninfo:
            raise EnvironmentError("LOTTO_DATABASE environment variable is not set") 
        self.__database = psycopg.connect(conninfo=conninfo)

    def get_latest_game(self, game_type: str) -> int:
        cursor = self.__database.cursor()
        cursor.execute("SELECT max(game) FROM games WHERE type=%s;", (game_type,))
        (result,) = cursor.fetchone()
        cursor.close()
        return result

    def get_games(self, game_type: str, count: int):
        cursor = self.__database.cursor()
        cursor.execute("SELECT game, numbers, supplementaries FROM sorted_games WHERE TYPE=%s ORDER BY game DESC LIMIT %s;", (game_type, count))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_games(self, game_type: str, from_game: int, to_game: int):
        cursor = self.__database.cursor()
        cursor.execute("SELECT game, numbers, supplementaries FROM sorted_games WHERE type=%s AND game BETWEEN %s AND %s ORDER BY game DESC", (game_type, from_game, to_game))
        result = cursor.fetchall()
        cursor.close()
        return result

    def add(self, game_type: str, game_number: int, numbers: list[int], supplementaries: list[int]):
        cursor = self.__database.cursor()
        cursor.execute(f"INSERT INTO games (type, game, numbers, supplementaries) VALUES (%s, %s, %s, %s);",
            (game_type, game_number, numbers, supplementaries))
        cursor.close()

    def commit(self):
        self.__database.commit()

    def close(self):
        self.__database.close()
