from CvPythonExtensions import *
gc = CyGlobalContext()

class Trophy:
	def __init__(self,name,description,enabledDDS,disabledDDS):
		self.name=name
		self.description=description
		self.enabledDDS = enabledDDS
		self.disabledDDS = disabledDDS
		self.has = False

ALL_TROPHIES = None

def init():
	global ALL_TROPHIES
	if not ALL_TROPHIES:
		ALL_TROPHIES=[
			Trophy("TROPHY_DEFEATED_ACHERON",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_ACHERON", ()),'art/interface/buttons/units/Acheron.dds','art/interface/buttons/trophies/AcheronGrey.dds'),
			Trophy("TROPHY_DEFEATED_ARS",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_ARS", ()),'art/interface/buttons/units/Ars.dds','art/interface/buttons/trophies/ArsGrey.dds'),
			Trophy("TROPHY_DEFEATED_BASIUM",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_BASIUM", ()),'art/interface/buttons/units/Basium.dds','art/interface/buttons/trophies/BasiumGrey.dds'),
			Trophy("TROPHY_DEFEATED_BUBOES",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_BUBOES", ()),'art/interface/buttons/units/Buboes.dds','art/interface/buttons/trophies/BuboesGrey.dds'),
			Trophy("TROPHY_DEFEATED_HYBOREM",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_HYBOREM", ()),'art/interface/buttons/units/Hyborem.dds','art/interface/buttons/trophies/HyboremGrey.dds'),
			Trophy("TROPHY_DEFEATED_LEVIATHAN",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_LEVIATHAN", ()),'art/interface/buttons/units/Leviathan.dds','art/interface/buttons/trophies/LeviathanGrey.dds'),
			Trophy("TROPHY_DEFEATED_ORTHUS",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_ORTHUS", ()),'art/interface/buttons/units/Orthus.dds','art/interface/buttons/trophies/OrthusGrey.dds'),
			Trophy("TROPHY_DEFEATED_STEPHANOS",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_STEPHANOS", ()),'art/interface/buttons/units/Stephanos.dds','art/interface/buttons/trophies/StephanosGrey.dds'),
			Trophy("TROPHY_DEFEATED_YERSINIA",CyTranslator().getText("TXT_KEY_TROPHY_DEFEATED_YERSINIA", ()),'art/interface/buttons/units/Yersinia.dds','art/interface/buttons/trophies/YersiniaGrey.dds'),
			Trophy("TROPHY_FEAT_APOCALYPSE",CyTranslator().getText("TXT_KEY_TROPHY_FEAT_APOCALYPSE", ()),'art/interface/buttons/Apocalypse.dds','art/interface/buttons/trophies/ApocalypseGrey.dds'),
			Trophy("TROPHY_FEAT_ASCENSION",CyTranslator().getText("TXT_KEY_TROPHY_FEAT_ASCENSION", ()),'art/interface/buttons/units/Auric Ascended.dds','art/interface/buttons/trophies/Auric AscendedGrey.dds'),
			Trophy("TROPHY_FEAT_BABOON",CyTranslator().getText("TXT_KEY_TROPHY_FEAT_BABOON", ()),'art/interface/buttons/units/Margalard.dds','art/interface/buttons/trophies/BaboonGrey.dds'),
			Trophy("TROPHY_FEAT_FLESH_GOLEM_15",CyTranslator().getText("TXT_KEY_TROPHY_FEAT_FLESH_GOLEM_15", ()),'art/interface/buttons/units/Flesh Golem.dds','art/interface/buttons/trophies/Flesh Golem15Grey.dds'),
			Trophy("TROPHY_FEAT_GODSLAYER",CyTranslator().getText("TXT_KEY_TROPHY_FEAT_GODSLAYER", ()),'art/interface/buttons/equipment/Godslayer.dds','art/interface/buttons/trophies/GodslayerGrey.dds'),
			Trophy("TROPHY_FEAT_GRAND_MENAGERIE",CyTranslator().getText("TXT_KEY_TROPHY_FEAT_GRAND_MENAGERIE", ()),'art/interface/buttons/buildings/Grand Menagerie.dds','art/interface/buttons/trophies/Grand MenagerieGrey.dds'),
			Trophy("TROPHY_FEAT_MIMIC_20",CyTranslator().getText("TXT_KEY_TROPHY_FEAT_MIMIC_20", ()),'art/interface/buttons/units/Mimic.dds','art/interface/buttons/trophies/Mimic20Grey.dds'),
			Trophy("TROPHY_FEAT_RESCUE_BRIGIT",CyTranslator().getText("TXT_KEY_TROPHY_FEAT_RESCUE_BRIGIT", ()),'art/interface/buttons/units/Brigit.dds','art/interface/buttons/trophies/BrigitGrey.dds'),
			Trophy("TROPHY_VICTORY_AMURITES",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_AMURITES", ()),'art/interface/TeamColor/Amuritesbutton.dds','art/interface/buttons/trophies/AmuritesGrey.dds'),
			Trophy("TROPHY_VICTORY_BALSERAPHS",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_BALSERAPHS", ()),'art/interface/TeamColor/Balseraphsbutton.dds','art/interface/buttons/trophies/BalseraphsGrey.dds'),
			Trophy("TROPHY_VICTORY_BANNOR",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_BANNOR", ()),'art/interface/TeamColor/Bannorbutton.dds','art/interface/buttons/trophies/BannorGrey.dds'),
			Trophy("TROPHY_VICTORY_CALABIM",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_CALABIM", ()),'art/interface/TeamColor/Calabimbutton.dds','art/interface/buttons/trophies/CalabimGrey.dds'),
			Trophy("TROPHY_VICTORY_CLAN_OF_EMBERS",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_CLAN_OF_EMBERS", ()),'art/interface/TeamColor/Clanofembersbutton.dds','art/interface/buttons/trophies/ClanofembersGrey.dds'),
			Trophy("TROPHY_VICTORY_DOVIELLO",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_DOVIELLO", ()),'art/interface/TeamColor/Doviellobutton.dds','art/interface/buttons/trophies/DovielloGrey.dds'),
			Trophy("TROPHY_VICTORY_ELOHIM",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_ELOHIM", ()),'art/interface/TeamColor/Elohimbutton.dds','art/interface/buttons/trophies/ElohimGrey.dds'),
			Trophy("TROPHY_VICTORY_GRIGORI",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_GRIGORI", ()),'art/interface/TeamColor/Grigoributton.dds','art/interface/buttons/trophies/GrigoriGrey.dds'),
			Trophy("TROPHY_VICTORY_HIPPUS",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_HIPPUS", ()),'art/interface/TeamColor/Hippusbutton.dds','art/interface/buttons/trophies/HippusGrey.dds'),
			Trophy("TROPHY_VICTORY_ILLIANS",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_ILLIANS", ()),'art/interface/TeamColor/Illiansbutton.dds','art/interface/buttons/trophies/IlliansGrey.dds'),
			Trophy("TROPHY_VICTORY_INFERNAL",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_INFERNAL", ()),'art/interface/TeamColor/Infernalbutton.dds','art/interface/buttons/trophies/InfernalGrey.dds'),
			Trophy("TROPHY_VICTORY_KHAZAD",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_KHAZAD", ()),'art/interface/TeamColor/Khazadbutton.dds','art/interface/buttons/trophies/KhazadGrey.dds'),
			Trophy("TROPHY_VICTORY_KURIOTATES",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_KURIOTATES", ()),'art/interface/TeamColor/Kuriotatesbutton.dds','art/interface/buttons/trophies/KuriotatesGrey.dds'),
			Trophy("TROPHY_VICTORY_LANUN",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_LANUN", ()),'art/interface/TeamColor/Lanunbutton.dds','art/interface/buttons/trophies/LanunGrey.dds'),
			Trophy("TROPHY_VICTORY_LJOSALFAR",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_LJOSALFAR", ()),'art/interface/TeamColor/Ljosalfarbutton.dds','art/interface/buttons/trophies/LjosalfarGrey.dds'),
			Trophy("TROPHY_VICTORY_LUCHUIRP",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_LUCHUIRP", ()),'art/interface/TeamColor/Luchuirpbutton.dds','art/interface/buttons/trophies/LuchuirpGrey.dds'),
			Trophy("TROPHY_VICTORY_MALAKIM",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_MALAKIM", ()),'art/interface/TeamColor/Malakimbutton.dds','art/interface/buttons/trophies/MalakimGrey.dds'),
			Trophy("TROPHY_VICTORY_MERCURIANS",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_MERCURIANS", ()),'art/interface/TeamColor/Mercuriansbutton.dds','art/interface/buttons/trophies/MercuriansGrey.dds'),
			Trophy("TROPHY_VICTORY_SHEAIM",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_SHEAIM", ()),'art/interface/TeamColor/Sheaimbutton.dds','art/interface/buttons/trophies/SheaimGrey.dds'),
			Trophy("TROPHY_VICTORY_SIDAR",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_SIDAR", ()),'art/interface/TeamColor/Sidarbutton.dds','art/interface/buttons/trophies/SidarGrey.dds'),
			Trophy("TROPHY_VICTORY_SVARTALFAR",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_SVARTALFAR", ()),'art/interface/TeamColor/Svartalfarbutton.dds','art/interface/buttons/trophies/SvartalfarGrey.dds'),
			Trophy("TROPHY_VICTORY_ALTAR_OF_THE_LUONNOTAR",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_ALTAR_OF_THE_LUONNOTAR", ()),'art/interface/buttons/buildings/AltaroftheLuonnotar.dds','art/interface/buttons/trophies/AltaroftheLuonnotarGrey.dds'),
			Trophy("TROPHY_VICTORY_CONQUEST",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_CONQUEST", ()),'art/interface/buttons/trophies/Conquest.dds','art/interface/buttons/trophies/ConquestGrey.dds'),
			Trophy("TROPHY_VICTORY_CULTURAL",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_CULTURAL", ()),'art/interface/buttons/trophies/Cultural.dds','art/interface/buttons/trophies/CulturalGrey.dds'),
			Trophy("TROPHY_VICTORY_DOMINATION",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_DOMINATION", ()),'art/interface/buttons/trophies/Domination.dds','art/interface/buttons/trophies/DominationGrey.dds'),
			Trophy("TROPHY_VICTORY_RELIGIOUS",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_RELIGIOUS", ()),'art/interface/buttons/promotions/divine.dds','art/interface/buttons/trophies/ReligiousGrey.dds'),
			Trophy("TROPHY_VICTORY_SCORE",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_SCORE", ()),'art/interface/buttons/trophies/Score.dds','art/interface/buttons/trophies/ScoreGrey.dds'),
			Trophy("TROPHY_VICTORY_TIME",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_TIME", ()),'art/interface/buttons/trophies/Time.dds','art/interface/buttons/trophies/TimeGrey.dds'),
			Trophy("TROPHY_VICTORY_TOWER_OF_MASTERY",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_TOWER_OF_MASTERY", ()),'art/interface/buttons/buildings/TowerofMastery.dds','art/interface/buttons/trophies/TowerofMasteryGrey.dds'),
			Trophy("TROPHY_VICTORY_BARBARIAN_WORLD",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_BARBARIAN_WORLD", ()),'art/interface/buttons/trophies/Barbarian World.dds','art/interface/buttons/trophies/Barbarian WorldGrey.dds'),
			Trophy("TROPHY_VICTORY_FINAL_FIVE",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_FINAL_FIVE", ()),'art/interface/buttons/trophies/Final Five.dds','art/interface/buttons/trophies/Final FiveGrey.dds'),
			Trophy("TROPHY_VICTORY_HIGH_TO_LOW",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_HIGH_TO_LOW", ()),'art/interface/buttons/trophies/High to Low.dds','art/interface/buttons/trophies/High to LowGrey.dds'),
			Trophy("TROPHY_VICTORY_INCREASING_DIFFICULTY",CyTranslator().getText("TXT_KEY_TROPHY_VICTORY_INCREASING_DIFFICULTY", ()),'art/interface/buttons/promotions/weak.dds','art/interface/buttons/trophies/Increasing DifficultyGrey.dds'),
			Trophy("TROPHY_WB_AGAINST_THE_GREY",CyTranslator().getText("TXT_KEY_WB_AGAINST_THE_GREY", ()),'art/interface/buttons/trophies/Against the Grey.dds','art/interface/buttons/trophies/Against the GreyGrey.dds'),
			Trophy("TROPHY_WB_AGAINST_THE_WALL",CyTranslator().getText("TXT_KEY_WB_AGAINST_THE_WALL", ()),'art/interface/buttons/trophies/Against the Wall.dds','art/interface/buttons/trophies/Against the WallGrey.dds'),
			Trophy("TROPHY_WB_BARBARIAN_ASSAULT",CyTranslator().getText("TXT_KEY_WB_BARBARIAN_ASSAULT", ()),'art/interface/buttons/trophies/Barbarian Assault.dds','art/interface/buttons/trophies/Barbarian AssaultGrey.dds'),
			Trophy("TROPHY_WB_BENEATH_THE_HEEL",CyTranslator().getText("TXT_KEY_WB_BENEATH_THE_HEEL", ()),'art/interface/buttons/trophies/Beneath the Heel.dds','art/interface/buttons/trophies/Beneath the HeelGrey.dds'),
			Trophy("TROPHY_WB_BLOOD_OF_ANGELS",CyTranslator().getText("TXT_KEY_WB_BLOOD_OF_ANGELS", ()),'art/interface/buttons/trophies/Blood of Angels.dds','art/interface/buttons/trophies/Blood of AngelsGrey.dds'),
			Trophy("TROPHY_WB_FALL_OF_CUANTINE",CyTranslator().getText("TXT_KEY_WB_FALL_OF_CUANTINE", ()),'art/interface/buttons/trophies/The Fall of Cuantine.dds','art/interface/buttons/trophies/The Fall of CuantineGrey.dds'),
			Trophy("TROPHY_WB_GIFT_OF_KYLORIN",CyTranslator().getText("TXT_KEY_WB_GIFT_OF_KYLORIN", ()),'art/interface/buttons/trophies/Gift of Kylorin.dds','art/interface/buttons/trophies/Gift of KylorinGrey.dds'),
			Trophy("TROPHY_WB_GRAND_MENAGERIE",CyTranslator().getText("TXT_KEY_WB_GRAND_MENAGERIE", ()),'art/interface/buttons/trophies/Grand Menagerie.dds','art/interface/buttons/trophies/Grand MenagerieGrey.dds'),
			Trophy("TROPHY_WB_INTO_THE_DESERT",CyTranslator().getText("TXT_KEY_WB_INTO_THE_DESERT", ()),'art/interface/buttons/trophies/Into the Desert.dds','art/interface/buttons/trophies/Into the DesertGrey.dds'),
			Trophy("TROPHY_WB_LORD_OF_THE_BALORS",CyTranslator().getText("TXT_KEY_WB_LORD_OF_THE_BALORS", ()),'art/interface/buttons/trophies/Lord of the Balors.dds','art/interface/buttons/trophies/Lord of the BalorsGrey.dds'),
			Trophy("TROPHY_WB_MULCARN_REBORN",CyTranslator().getText("TXT_KEY_WB_MULCARN_REBORN", ()),'art/interface/buttons/trophies/Mulcarn Reborn.dds','art/interface/buttons/trophies/Mulcarn RebornGrey.dds'),
			Trophy("TROPHY_WB_RETURN_OF_WINTER",CyTranslator().getText("TXT_KEY_WB_RETURN_OF_WINTER", ()),'art/interface/buttons/trophies/Return of Winter.dds','art/interface/buttons/trophies/Return of WinterGrey.dds'),
			Trophy("TROPHY_WB_THE_BLACK_TOWER",CyTranslator().getText("TXT_KEY_WB_THE_BLACK_TOWER", ()),'art/interface/buttons/trophies/The Black Tower.dds','art/interface/buttons/trophies/The Black TowerGrey.dds'),
			Trophy("TROPHY_WB_THE_CULT",CyTranslator().getText("TXT_KEY_WB_THE_CULT", ()),'art/interface/buttons/trophies/The Cult.dds','art/interface/buttons/trophies/The CultGrey.dds'),
			Trophy("TROPHY_WB_THE_MOMUS",CyTranslator().getText("TXT_KEY_WB_THE_MOMUS", ()),'art/interface/buttons/trophies/The Momus.dds','art/interface/buttons/trophies/The MomusGrey.dds'),
			Trophy("TROPHY_WB_THE_RADIANT_GUARD",CyTranslator().getText("TXT_KEY_WB_THE_RADIANT_GUARD", ()),'art/interface/buttons/trophies/The Radiant Guard.dds','art/interface/buttons/trophies/The Radiant GuardGrey.dds'),
			Trophy("TROPHY_WB_THE_SPLINTERED_COURT",CyTranslator().getText("TXT_KEY_WB_THE_SPLINTERED_COURT", ()),'art/interface/buttons/trophies/The Splintered Court.dds','art/interface/buttons/trophies/The Splintered CourtGrey.dds'),
			Trophy("TROPHY_WB_WAGES_OF_SIN",CyTranslator().getText("TXT_KEY_WB_WAGES_OF_SIN", ()),'art/interface/buttons/trophies/Wages of Sin.dds','art/interface/buttons/trophies/Wages of SinGrey.dds')
			]

def update():
	for t in ALL_TROPHIES:
		if CyGame().isHasTrophy(t.name):
			t.has=True
