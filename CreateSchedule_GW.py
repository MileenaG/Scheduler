import Constants
from Observatory import Observatory
from Telescope import Swope, Nickel
from Utilities import *
from Target import TargetType, Target

from dateutil.parser import parse
import argparse
from astropy.coordinates import SkyCoord
from astropy import units as unit

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file", help="CSV file with targets to schedule.")
	parser.add_argument("-d", "--date", help="YYYYMMDD formatted observation date.")
	parser.add_argument("-ot", "--obstele", help="Comma-delimited list of <Observatory>:<Telescope>, to schedule targets.")
	args = parser.parse_args()

	file_name = args.file
	obs_date = args.date
	observatory_telescopes = args.obstele.split(",")
	
	obs_keys = [o.split(":")[0] for o in observatory_telescopes]
	tele_keys = [t.split(":")[1] for t in observatory_telescopes]

	lco = Observatory(
		name="LCO",
		lon="-70.6915",
		lat="-29.0182",
		elevation=2402,
		horizon="-12",
		telescopes={"Swope":Swope()},
		obs_date_str=obs_date,
		utc_offset=lco_clst_utc_offset,
		utc_offset_name="CLST"
	)

	lick = Observatory(
		name="Lick",
		lon="-121.6429",
		lat="37.3414",
		elevation=1283,
		horizon="-12",
		telescopes={"Nickel":Nickel()},
		obs_date_str=obs_date,
		utc_offset=lick_pst_utc_offset,
		utc_offset_name="PST"
	)
#Literal Dictionary
	observatories = {"LCO":lco, "Lick":lick}   #"LCO" string #lco is a variable observatory object
    #columns in input csv file
	target_data = get_targets("%s" % file_name)    #parsing data 
	names = [t[0] for t in target_data]
	ra = [t[1] for t in target_data]
	dec = [t[2] for t in target_data]
	priorities = [float(t[3]) for t in target_data]         
	disc_dates = [t[4] for t in target_data]
	disc_mags = [float(t[5]) for t in target_data] 
	types = [t[6] for t in target_data]                        
	static_exposure_time = [float(t[7]) for t in target_data]
	EstAbsMag = [float(t[8]) for t in target_data]    #assuing they're 18
	dist_Mpc = [float(t[9]) for t in target_data]
	#dynamic_exposure_times = [t[10] for t in target_data]
	#Apparent_Mag = [t[11] for t in target_data]             #empty lists. no data yet


	coords = SkyCoord(ra,dec,unit=(unit.hour, unit.deg)) #returns list or array from astropy

	for i in range(len(observatory_telescopes)):   #loops over everything in the observatories dictionary 
		
		targets = []                               #empty list
		obs = observatories[obs_keys[i]]

		for j in range(len(names)):
			target_type = None
			disc_date = None
			if types[j] == "STD":
				target_type = TargetType.Standard
				disc_date = None
			elif types[j] == "TMP":
				target_type = TargetType.Template
				disc_date = parse(disc_dates[j])
			elif types[j] == "SN":
				target_type = TargetType.Supernova
				disc_date = parse(disc_dates[j]) 
			elif types[j] == "GWS":
				target_type = TargetType.GWS
				disc_date = parse(disc_dates[j]) 
			elif types[j] == "GWD":
				target_type = TargetType.GWD
				disc_date = parse(disc_dates[j])
			else:
				raise ValueError('Unrecognized target type!')

			targets.append(                                    #adding to targets list
				Target(
					name=names[j], 
					coord=coords[j], 
					priority=priorities[j], 
					target_type=target_type, 
					observatory_lat=obs.ephemeris.lat, 
					sidereal_radian_array=obs.sidereal_radian_array, 
					disc_date=disc_date, 
					apparent_mag=disc_mags[j], 
					obs_date=obs.obs_date,
					static_exposure_time=static_exposure_time[j], 
					#dynamic_exposure_time=dynamic_exposure_time[j],
					#Apparent_Mag=Apparent_Mag[j],
					EstAbsMag=EstAbsMag[j],
					dist_Mpc=dist_Mpc[j]
									)
			)

			obs.telescopes[tele_keys[i]].set_targets(targets) #reference to the vaules in the obervatory object 

		print("# of %s targets: %s" % (tele_keys[i], len(targets)))
		print("First %s target: %s" % (tele_keys[i], targets[0].name))
		print("Last %s target: %s" % (tele_keys[i], targets[-1].name))

		obs.schedule_targets(tele_keys[i])            #goes thru the next observatory until we've gone thru all of them

	exit = input("\n\nENTER to exit")

if __name__ == "__main__": main()

		
