import os
import traceback
from discord.ext import commands
import logging
import datetime
import sys

def config_logging(args):
    levelmapping = {"-v":[logging.DEBUG, "Debug logging enabled."], "--debug":[logging.DEBUG, "Debug logging enabled."], "--verbose":[logging.DEBUG, "Debug logging enabled."], "-i":[logging.INFO, "Logging level set to INFO."], "--info":[logging.INFO, "Logging level set to INFO"], "-w":[logging.WARN, "Logging level set to WARN."], "--warn":[logging.WARN, "Logging level set to WARN."], "-e":[logging.ERROR, "Logging level set to ERROR."], "--error":[logging.ERROR, "Logging level set to ERROR."], "-q":["disable", "Logging disabled. Tracebacks will still be shown in the console, along with a few status messages."], "--quiet":["disable", "Logging disabled. Tracebacks will still be shown in the console, along with a few status messages."]}
    for key, value in levelmapping.items():
        if key not in args:
            pass
        elif key in args and key != "-q" and key != "--quiet":
            logging.basicConfig(level=value[0], handlers=[logging.FileHandler(f"logs/maximilian-{datetime.date.today()}.log"), logging.StreamHandler(sys.stdout)])
            logging.getLogger("maximilian.init.config_logging").warning(f"Logging started at {datetime.datetime.now()}")
            print(value[1])
            return
        else:
            logging.disable()
            print(value[1])
            return
    logging.basicConfig(level=logging.WARN, handlers=[logging.FileHandler(f"logs/maximilian-{datetime.date.today()}.log"), logging.StreamHandler(sys.stdout)])
    print("No logging level specified, falling back to WARN.")
    logging.getLogger("maximilian.init.config_logging").warning(f"Logging started at {datetime.datetime.now()}")

class init():
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(f"maximilian.{__name__}")

    def parse_arguments(self, args):
        if len(args) > 1:
            if "--ip" in args:
                try:
                    self.bot.dbip = args[args.index("--ip")+1]
                    self.logger.info(f"Set database IP address to {self.bot.dbip}.")
                except ValueError:
                    self.logger.warning("You need to specify what ip address you want to use with the database. Since you didn't specify an IP address, I'll fall back to using localhost.")
                    self.bot.dbip = "localhost"
            else:
                self.logger.warning("No database IP provided. Falling back to localhost.")
                self.bot.dbip = "localhost"
            if "--enablejsk" in args:
                self.bot.load_extension("jishaku")
                self.logger.info("Loaded Jishaku.")
        else:
            self.logger.warning("No database IP provided. Falling back to localhost.")
            self.bot.dbip = "localhost"

    def load_extensions(self):
        self.logger.debug("Loading extensions...")
        extensioncount, errorcount = 0, 0
        for each in os.listdir("./cogs"):
            if each.endswith(".py"):
                try:
                    self.bot.load_extension(f"cogs.{each[:-3]}")
                    extensioncount += 1
                    self.logger.info(f"Loaded cogs.{each[:-3]}.")
                except commands.ExtensionAlreadyLoaded:
                    self.logger.info(f"{each[:-3]} is already loaded, skipping")
                except commands.ExtensionFailed as error:
                    errorcount += 1
                    self.logger.error(f"{type(error.original).__name__} while loading '{error.name}'. {'Run Maximilian again with the -v command line argument to show additional information.' if type(error.original).__name__ == 'SyntaxError' else ''}")
                    if isinstance(error.original, SyntaxError):
                        self.logger.debug(traceback.format_exc())
                    elif isinstance(error.original, ModuleNotFoundError) or isinstance(error.original, ImportError):
                        self.logger.error(f"The {error.original.name} module isn't installed, '{error.name}' won't be loaded")
        #create instances of certain cogs
        try:
            self.bot.coreinst = self.bot.get_cog('core')
            self.bot.prefixesinst = self.bot.get_cog('prefixes')
            self.bot.responsesinst = self.bot.get_cog('Custom Commands')
            self.bot.miscinst = self.bot.get_cog('misc')
            self.bot.reactionrolesinst = self.bot.get_cog('reaction roles')
        except:
            self.logger.error("Failed to get one or more cogs, some stuff might not work.")
        self.logger.info(f"loaded {extensioncount} extensions successfully{f' ({errorcount} extension(s) not loaded)'}, waiting for ready")
