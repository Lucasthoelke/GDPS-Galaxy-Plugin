# == TODO ==
# 1. Move from Requests to galaxy.http
# == KNOWN BUGS ==

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LicenseType, LocalGameState
from galaxy.api.types import Authentication, Game, LocalGame, LicenseInfo
import sys
import logging
import logging.handlers
import urllib.request
import json
import requests
import time
import asyncio

class GDPSPlugin(Plugin):
	def __init__(self, reader, writer, token):
		super().__init__(Platform.Newegg, "0.1", reader, writer, token)

		self.checking_for_new_games = False
		self.checking_for_removed_games = False

		self.owned_games_cache = []

		self.last_unix_tick = 0

	# Custom Functions
	def __do_auth__(self):
		user_data = {}
		user_data['username'] = 'GDPS'
		user_data['ID'] = "GDPS_User_ID"

		self.store_credentials(user_data)
		return Authentication(user_data['ID'], user_data["username"])

	async def __check_for_new_games__(self): #Return list of new games
		self.checking_for_new_games = True
		# DO STUFF
		self.checking_for_new_games = False

	async def __check_for_removed_games__(self): #Return list of games to be removed
		self.checking_for_removed_games = True
		# DO STUFF
		self.checking_for_removed_games = False

	def __get_games_from_gdps__(self):

		games = []

		contents = requests.get("http://localhost/GDPS/api.php?module=gdps&func=get_available_games")

		logging.info("<<GDPS>> Requested games...")
		#logging.info(contents.text)

		parsed = json.loads(contents.text)

		logging.info(parsed['message'])
		
		for game in parsed['message']:
			games.append( Game( "A"+game['game_id'], game['game_name'], None, LicenseInfo( LicenseType.SinglePurchase, None ) ) )

		return games

	#Override functions
	async def authenticate(self, stored_credentials=None):
		return self.__do_auth__()

	async def pass_login_credentials(self, step, credentials, cookies):
		return self.__do_auth__()

	async def get_owned_games(self):
		#owned_games = [Game("G2", "GrandTheftAutoV", None, LicenseInfo(LicenseType.SinglePurchase, None))]
		owned_games = self.__get_games_from_gdps__()
		self.owned_games_cache = owned_games

		# DEBUG

		#owned_games.append( Game( "G0", "GreedFall", None, LicenseInfo( LicenseType.SinglePurchase, None ) ) )
		#owned_games.append( Game( "G1", "Minecraft", None, LicenseInfo( LicenseType.SinglePurchase, None ) ) )
		#self.owned_games_cache = owned_games

		logging.info("<<DEBUG>> Owned games:")
		for game in owned_games:
			logging.info("<DEBUG>>     " + game.game_title)

		# DEBUG END

		return owned_games

	def handshake_complete(self):
		pass

	def tick(self):
		if self.last_unix_tick + 5 < int(time.time()): #Wait 30 seconds before refreshing, DEBUG: 5 seconds
			self.last_unix_tick = int(time.time())
			logging.info("Checking for new game info")

			# DEBUG

			logging.info("<<DEBUG>> Local Cache:")
			for game in self.owned_games_cache:
				logging.info("<<DEBUG>>     " + game.game_title + " : " + game.game_id)

			# DEBUG END

			if not self.checking_for_new_games:
				pass#asyncio.create_task(self.__check_for_new_games__())
			if not self.checking_for_removed_games:
				pass#asyncio.create_task(self.__check_for_removed_games__())



def main():
	create_and_run_plugin(GDPSPlugin, sys.argv)

if __name__ == "__main__":
	main()