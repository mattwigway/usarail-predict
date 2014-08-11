from sqlalchemy.orm import sessionmaker
from time import sleep
from urllib2 import urlopen
from json import load, loads
from datetime import date

from schema import *
from dbconn import dbConnect

debug = False

eng = dbConnect()
Session = sessionmaker(bind=eng)
sess = Session()

# create database tables
Base.metadata.create_all(eng)


# pull down the GeoJSON that drives Amtrak's home page map
# incidentally, this is not forbidden by robots.txt :)
data = load(urlopen('https://www.googleapis.com/mapsengine/v1/tables/01382379791355219452-08584582962951999356/features?version=published&key=AIzaSyCVFeFQrtk-ywrUE0pEcvlwgCqS6TJcOW4&maxResults=250&dataType=json&contentType=application%2Fjson'))
#data = load(urlopen('http://localhost:8000/in.json'))

# loop over each train
for feat in data['features']:
    props = feat['properties']
    # find the train number or create it
    rt = sess.query(Route).filter_by(number=props['TrainNum']).first()

    if rt == None:
        rt = Route(
            number = props['TrainNum'],
            name = props['RouteName']
        )
        sess.add(rt)

    rawDate = props['OrigSchDep'][:10].strip().split('/')
    depDate = date(int(rawDate[2]), int(rawDate[0]), int(rawDate[1]))

    # find the appropriate train
    tr = sess.query(Train).filter_by(route=rt, depDate=depDate).first()

    if tr == None:
        tr = Train(
            trainNumber = rt.number,
            depDate = depDate)
        sess.add(tr)

    if tr.completed:
        # train has arrived at its final destination, no need to continue to update
        continue

    # create a TrainStatus entry
    ts = TrainStatus(
        trainId = tr.fid,
        velocity = float(props['Velocity']) if props.has_key('Velocity') and props['Velocity'] != '' else None,
        status = props['TrainState'],
        retrieved = datetime.now(),
        the_geom = 'POINT(%s %s)' % tuple(feat['geometry']['coordinates'])
    )

    sess.add(ts)

    completed = True

    # Create StationStatus entries
    for key in [k for k in props.keys() if k.startswith('Station')]:
        rawss = loads(props[key])
        # check if this station status already exists
        if rawss.has_key('postdep') and rawss['postdep'] != '':
            if sess.query(StationStatus).filter(StationStatus.actDep != None,
                                                StationStatus.stationId == rawss['code'],
                                                StationStatus.trainStatus == tr)\
                                        .count() > 0:
                # this train arrived at this station in the past, don't record it again
                continue
        else:
            completed = False

        # create the station if need be
        if sess.query(Station).filter(Station.code==rawss['code']).count() == 0:
            sta = Station(
                code = rawss['code']
                # for now leave this stuff blank, fix later
                )
            sess.add(sta)
            
        ss = StationStatus(
            number = int(key[7:]),
            schedArr = rawss['scharr'] if rawss.has_key('scharr') else None,
            schedDep = rawss['schdep'] if rawss.has_key('schdep') else None,
            estArr = rawss['estarr'] if rawss.has_key('estarr') else None,
            estDep = rawss['estdep'] if rawss.has_key('estdep') else None,
            actArr = rawss['postarr'] if rawss.has_key('postarr') else None,
            actDep = rawss['postdep'] if rawss.has_key('postdep') else None,
            trainStatusId = ts.fid,
            stationId = rawss['code']
        )
        sess.add(ss)

    if completed:
        ts.completed = True
        sess.add(ts)

# save our work
sess.commit()
