# supreme_profile.py
# used in: Supreme with Cheese
# file extension: .prf
# Supreme player profile format (unfinished)

from sformats.utils import *

# from Supreme source

# PADDING!

# typedef struct levelData_t	// contains your scores, etc for one level
# {
# byte levelNum;		// because only passed levels are stored
# byte flags;
# float percentage;
# float recordDestroy;
# int   recordCombo;
# dword recordBaseScore;
# } levelData_t;

# typedef struct worldData_t	// contains your progress for one world
# {
# char filename[32];	// the world's filename
# int  var[8];		// the 'global' variables for this world
# byte keychains;		// bitflags for each one, and the loonykey
# float percentage;
# byte levelOn;		// which level of this world you're on
# byte levels;		// how many levels are stored here - it only stores ones you've either
# 					// passed, or accomplished something in
# levelData_t *level;	// progress info for each level that HAS been passed only.
# } worldData_t;

# EXPANSION_SIZE 1019

# typedef struct progress_t
# {
# // total values for stats
# dword totalCandles;
# dword totalBrains;
# dword totalTime;
# dword totalCoins,coinsSpent;
# dword totalWorlds;
# dword loonyKeys,loonyKeysUsed;
# float totalPercent;	// percentage of ALL worlds/levels/etc you have completed

# dword hammersThrown;
# dword damageDone,damageTaken;
# dword shotsFired;
# dword rages;
# dword runOver;
# word finishedWorlds;	// worlds you've 100%ed
# dword footDistance,raftDistance,cartDistance,driveDistance;
# dword underwaterTime;
# dword grassChopped;
# dword keysFound,doorsOpened;
# dword calories,calsBurned;
# word  bestCombo;

# int num_worlds;
# worldData_t *world;
# word kills[NUM_MONSTERS];	// how many times you've killed each type
# byte scanned[NUM_MONSTERS];	// has each type been scanned?
# byte purchase[256];			// which things you have purchased
# byte movie[20];				// which movies you've seen for theater purposes
# byte goal[100];				// whether you've done each of the 100 goals

# dword cheats;				// how often you've cheated
# byte wpnLock;				// weapon lock
# byte expansion[EXPANSION_SIZE];		// unused space for possible future expansion
# } progress_t;

# typedef struct playList_t
# {
# byte numSongs;
# char *song;
# } playList_t;

# typedef struct profile_t
# {
# char name[16];
# // important stuff
# byte control[2][6];	// key scancodes
# byte joyCtrl[2];	// joystick 'codes' for the buttons
# byte sound;			// sound volume
# byte music;			// music volume
# byte musicMode;		// music playing mode

# char lastWorld[32];	// name of the last world visited
# playList_t playList[NUM_PLAYLISTS];	// song playlists
# byte difficulty;
# byte playAs;
# byte moveNShoot,candleRadar,brainRadar;
# byte nameVerified;
# progress_t progress;
# char motd[1024];	// message of the day
# } profile_t;

# void SaveProfile(void)
# {
	# FILE *f;
	# int i,j;

	# f=fopen("profile.cfg","wt");
	# fprintf(f,"%s\n",profile.name);
	# fclose(f);
	
	# sprintf(prfName,"profiles/%s.prf",profile.name);
	# // also actually save the profile!
	# f=fopen(prfName,"wb");
	# fwrite(&profile,sizeof(profile_t),1,f);

	# SavePlayLists(f);

	# // to enforce the "TEST" world being present
	# GetWorldProgress("TEST");
	# // so that we can save the word!
	# for(i=0;i<profile.progress.num_worlds;i++)
	# {
		# fwrite(&profile.progress.world[i],sizeof(worldData_t),1,f);
		# for(j=0;j<profile.progress.world[i].levels;j++)
		# {
			# fwrite(&profile.progress.world[i].level[j],sizeof(levelData_t),1,f);
		# }
	# }
	# fclose(f);
	# firstTime=0;
# }

# void LoadProfile(char *name)
# {
	# FILE *f;
	# int i,j;

	# strcpy(profile.name,name);
	# sprintf(prfName,"profiles/%s.prf",profile.name);

	# // save this profile as the current one.
	# f=fopen("profile.cfg","wt");
	# fprintf(f,"%s\n",profile.name);
	# fclose(f);

	# // now load it
	# f=fopen(prfName,"rb");
	# if(!f)	// file doesn't exist
	# {
		# DefaultProfile(name);
		# return;
	# }
	# fread(&profile,sizeof(profile_t),1,f);
	# LoadPlayLists(f);
	
	# // fixed changed Mac OS X scancodes
	# for (int i = 0; i < 2; ++i)
		# for (int j = 0; j < 6; ++j)
			# if (profile.control[i][j] >= KEY_EQUALS_PAD && profile.control[i][j] <= KEY_COMMAND)
				# profile.control[i][j] += KEY_LSHIFT - KEY_EQUALS_PAD;

	# if(profile.progress.num_worlds==0)
		# profile.progress.world=NULL;
	# else
	# {
		# profile.progress.world=(worldData_t *)malloc(sizeof(worldData_t)*profile.progress.num_worlds);
		# for(i=0;i<profile.progress.num_worlds;i++)
		# {
			# fread(&profile.progress.world[i],sizeof(worldData_t),1,f);
			# profile.progress.world[i].level=(levelData_t *)malloc(sizeof(levelData_t)*profile.progress.world[i].levels);
			# for(j=0;j<profile.progress.world[i].levels;j++)
			# {
				# fread(&profile.progress.world[i].level[j],sizeof(levelData_t),1,f);
			# }
		# }
	# }
	# fclose(f);
# }

# structures

supreme_profile = Struct("supremeProfile")
