import obspy
from obspy.core.inventory import Inventory, Network, Station, Channel, Site
from obspy.clients.nrl import NRL


# We'll first create all the various objects. These strongly follow the
# hierarchy of StationXML files.
inv = Inventory(
    # We'll add networks later.
    networks=[],
    # The source should be the id whoever create the file.
    source="ERP")

net = Network(
    # This is the network code according to the SEED standard.
    code="CDMX",
    # A list of stations. We'll add one later.
    stations=[],
    description="A test stations.",
    # Start-and end dates are optional.
    start_date=obspy.UTCDateTime(2023, 1, 2))

sta = Station(
    # This is the station code according to the SEED standard.
    code="P010",
    latitude=19.358297,
    longitude=-99.192870,
    elevation=2290.0,
    creation_date=obspy.UTCDateTime(2023, 1, 2),
    site=Site(name="First station"))

cha = Channel(
    # This is the channel code according to the SEED standard.
    code="HHZ",
    # This is the location code according to the SEED standard.
    location_code="",
    # Note that these coordinates can differ from the station coordinates.
    latitude=19.358297,
    longitude=-99.192870,
    elevation=2290.0,
    depth=10.0,
    azimuth=0.0,
    dip=-90.0,
    sample_rate=100)

# By default this accesses the NRL online. Offline copies of the NRL can
# also be used instead
nrl = NRL()
# The contents of the NRL can be explored interactively in a Python prompt,
# see API documentation of NRL submodule:
# http://docs.obspy.org/packages/obspy.clients.nrl.html
# Here we assume that the end point of data logger and sensor are already
# known:
response = nrl.get_response( # doctest: +SKIP
    sensor_keys=['Guralp', 'CMG-6T', '30 seconds'],
    datalogger_keys=['Guralp', 'CMG-6TD', '1', '100'])


# Now tie it all together.
cha.response = response
sta.channels.append(cha)
net.stations.append(sta)
inv.networks.append(net)

# And finally write it to a StationXML file. We also force a validation against
# the StationXML schema to ensure it produces a valid StationXML file.
#
# Note that it is also possible to serialize to any of the other inventory
# output formats ObsPy supports.
inv.write("station.xml", format="stationxml", validate=True)