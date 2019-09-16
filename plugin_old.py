import sys
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LicenseType, LocalGameState
from galaxy.api.types import Authentication, Game, LocalGame, LicenseInfo
import logging
import logging.handlers
import urllib.request
import json
import requests
import time
import asyncio

class TestPlugin(Plugin):

	serverLoc = '127.0.0.1'
	serverApiKey = ''
	checking_for_new_games = False
	checking_for_removed_games = False
	owned_games_cache = []
	last_tick_unix = 0

	def __init__(self, reader, writer, token):
		super().__init__(Platform.Newegg, "0.1", reader, writer, token)

	async def authenticate(self, stored_credentials=None):
		return self.do_auth()


	async def pass_login_credentials(self, step, credentials, cookies):
		return self.do_auth()

	def do_auth(self):
		user_data = {}
		username = "GDPS" #Api key or something
		user_data["username"] = username
		self.store_credentials(user_data)
		return Authentication("test_user", user_data["username"])

	async def get_owned_games(self):
		#owned_games = [Game('69', 'Nice', None, LicenseInfo(LicenseType.SinglePurchase, None))]
		#owned_games = []
		owned_games = self.__get_games_from_gdps()
		self.owned_games_cache = owned_games

		for game in owned_games:
			logging.info("Owned game: " + game.game_title)

		return owned_games

	async def check_for_new_games(self):
		logging.info("Checking for new games...")
		self.checking_for_new_games = True
		games = await self.get_owned_games()
		for game in games:
			if game not in self.owned_games_cache:
				logging.info("Adding game: " + game.game_title)
				self.owned_games_cache.append(game)
				self.add_game(game)
		self.checking_for_new_games = False


	async def check_for_removed_games(self):
		logging.info("Checking for removed games...")
		self.checking_for_removed_games = True
		games = await self.get_owned_games()
		for game in self.owned_games_cache:
			if game not in self.owned_games_cache:
				logging.info("Removeing game: " + game.game_title)
				self.owned_games_cache.remove(game)
				self.remove_game(game.game_id)
		self.checking_for_removed_games = False




	def tick(self):

		if self.last_tick_unix + 30 < int(time.time()):
			self.last_tick_unix = int(time.time())
			logging.info("Checking for game changes...")

			logging.info("Current Cache:")
			for game in self.owned_games_cache:
				logging.info("Cache: " + game.game_title + " : " + game.game_id)

			if not self.checking_for_new_games:
				asyncio.create_task(self.check_for_new_games())
			if not self.checking_for_removed_games:
				asyncio.create_task(self.check_for_removed_games())
			#if not self.updating_game_statuses:
			#	asyncio.create_task(self.update_game_statuses())



	def handshake_complete(self):
		pass

	def __get_games_from_gdps(self):

		games = []

		contents = requests.get("http://localhost/GDPS/api.php?module=gdps&func=get_available_games")

		logging.info("GDPS Requested")
		logging.info(contents.text)

		parsed = json.loads(contents.text)

		logging.info(parsed['message'])
		
		for game in parsed['message']:
			games.append( Game( "GDPS" + game['game_id'], game['game_name'], None, LicenseInfo( LicenseType.SinglePurchase, None ) ) )

		return games



def main():
	create_and_run_plugin(TestPlugin, sys.argv)

if __name__ == "__main__":
    main()