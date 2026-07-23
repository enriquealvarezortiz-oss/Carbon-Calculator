import streamlit as st
import pandas as pd
import io
from math import radians, cos, sin, asin, sqrt
from geopy.geocoders import Nominatim

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Carbon Calculator", layout="wide")
st.title("🌍 Global Logistics Carbon Calculator")
st.write("Upload your shipment CSVs to automatically calculate your global CO₂e emissions.")

# --- 1. CONSTANTS & CACHE ---
PARAMS = {
    'Ocean':  {'factor': 0.17,  'multiplier': 1.2, 'weight': 10.875},
    'Air':    {'factor': 2.394, 'multiplier': 1.5, 'weight': 1.0},
    'Trucks': {'factor': 0.35,  'multiplier': 1.0, 'weight': 10.875}
}

# Cache the coordinates so the app is instantly fast for everyone
@st.cache_data
def get_coords_cache():
    return {
        "ROTTERDAM, NL": (4.47, 51.92), "NEW YORK, NY": (-74.00, 40.71), "GEORGETOWN, TN": (-84.89, 35.29),
        "ANTWERPEN, BE": (4.40, 51.21), "SPRINGFIELD, MO": (-93.29, 37.20), "KUMPORT, TR": (28.67, 40.97),
        "XINGANG, CN": (117.75, 38.98), "LONG BEACH, CA": (-118.19, 33.77), "INDIANAPOLIS, IN": (-86.15, 39.76),
        "KAOHSIUNG, TW": (120.30, 22.62), "LOS ANGELES, CA": (-118.24, 34.05), "CHARLESTON, SC": (-79.93, 32.77),
        "SHANGHAI, CN": (121.47, 31.23), "SAVANNAH, GA": (-81.09, 32.08), "ALPHARETTA, GA": (-84.29, 34.07),
        "YANTIAN, CN": (114.28, 22.58), "TAICHUNG, TW": (120.67, 24.14), "GENOA, IT": (8.94, 44.40), 
        "NORFOLK, VA": (-76.28, 36.85), "JACKSONVILLE, FL": (-81.65, 30.33), "MELBOURNE, AU": (144.96, -37.81),
        "HAMBURG, DE": (9.99, 53.55), "MONTREAL, CA": (-73.56, 45.50), "NINGBO, CN": (121.54, 29.87), 
        "HOUSTON, TX": (-95.36, 29.76), "SHREVEPORT, LA": (-93.75, 32.52), "GREER, SC": (-82.22, 34.93),
        "LIVERPOOL, GB": (-2.99, 53.40), "ONTARIO, CA": (-117.65, 34.06), "PORT HURON, MI": (-82.42, 42.97), 
        "TOLEDO, OH": (-83.55, 41.65), "SHENZHEN, CN": (114.05, 22.54), "SANTOS, BR": (-46.33, -23.96), 
        "PORT EVERGLADES, FL": (-80.11, 26.08), "MIAMI SPRINGS, FL": (-80.28, 25.82), "COLOMBO, LK": (79.86, 6.92), 
        "AKRON, OH": (-81.51, 41.08), "HALIFAX, CA": (-63.57, 44.64), "QINGDAO, CN": (120.38, 36.06), 
        "PHILADELPHIA, PA": (-75.16, 39.95), "OREFIELD, PA": (-75.58, 40.63), "DETROIT, MI": (-83.04, 42.33),
        "TAOYUAN, TW": (121.30, 24.99), "ATLANTA, GA": (-84.38, 33.74), "LOUISIANA, MO": (-91.05, 39.44),
        "BREMERHAVEN, DE": (8.58, 53.54), "CAI MEP, VN": (107.03, 10.53), "EULESS, TX": (-97.08, 32.83),
        "OSLO, NO": (10.75, 59.91), "NEWARK, NJ": (-74.17, 40.73), "NEW HOLLAND, PA": (-76.08, 40.10),
        "HAIPHONG, VN": (106.68, 20.84), "URBANDALE, IA": (-93.74, 41.62), "BLACK MOUNTAIN, NC": (-82.32, 35.61),
        "MIAMI, FL": (-80.19, 25.76), "LAKE PARK, FL": (-80.06, 26.79), "ALCESTER, GB": (-1.87, 52.21),
        "GDANSK, PL": (18.64, 54.35), "CHAGRIN FALLS, OH": (-81.39, 41.42), "BUSAN, KR": (129.07, 35.17), 
        "EMMAUS, PA": (-75.49, 40.53), "PORT KELANG, MY": (101.39, 3.03), "COCHIN, IN": (76.26, 9.93), 
        "SELLERSVILLE, PA": (-75.31, 40.35), "SALISBURY, NC": (-80.47, 35.66), "BAXTER, MN": (-94.28, 46.33),
        "BETHLEHEM, PA": (-75.38, 40.62), "MIDDLETOWN, PA": (-76.73, 40.19), "GUATEMALA CITY, GT": (-90.51, 14.63),
        "SOUTHAMPTON, GB": (-1.40, 50.90), "ALTAMIRA, MX": (-97.93, 22.39), "JALISCO, MX": (-103.34, 20.65),
        "GRAND RAPIDS, MN": (-93.52, 47.23), "HANNOVER, DE": (9.73, 52.37), "BRUNSWICK, GA": (-81.49, 31.14), 
        "MCDONOUGH, GA": (-84.14, 33.44), "GOTHENBURG | GOTEBORG, SE": (11.97, 57.70), "RIGA, LV": (24.10, 56.94),
        "DALLAS, TX": (-96.79, 32.77), "KLAIPEDA, LT": (21.14, 55.70), "CHICAGO, IL": (-87.62, 41.87),
        "MARYSVILLE, WA": (-122.17, 48.05), "ABBOTSFORD, CA": (-122.30, 49.05), "NHAVA SHEVA, IN": (72.95, 18.94),
        "NHAVA SHEVA (JAWAHARLAL NEHRU), IN": (72.95, 18.94), "BOLINGBROOK, IL": (-88.08, 41.69),
        "ISTANBUL, TR": (28.97, 41.00), "DALIAN, CN": (121.61, 38.91), "NASHVILLE, TN": (-86.78, 36.16),
        "POMPANO BEACH, FL": (-80.12, 26.23), "CALLAO, PE": (-77.14, -12.06), "WALTON, KY": (-84.60, 38.86),
        "KOBE, JP": (135.19, 34.69), "CULVER CITY, CA": (-118.39, 34.02), "MARBLEHEAD, MA": (-70.85, 42.50), 
        "HONG KONG, HK": (114.16, 22.31), "WATERTOWN, SD": (-97.11, 44.90), "SMYRNA, TN": (-86.51, 35.98),
        "TLAQUEPAQUE, MX": (-103.31, 20.64), "CAMP HILL, PA": (-76.92, 40.24), "CONYERS, GA": (-84.01, 33.66),
        "FREMONT, CA": (-121.98, 37.54), "OAKLAND, CA": (-122.27, 37.80), "TAIWAN": (120.96, 23.69),
        "JEBEL ALI, AE": (55.07, 24.98), "OSSIAN, IN": (-85.16, 40.87), "CHATEAUGUAY, CA": (-73.74, 45.36),
        "HENDERSONVILLE, NC": (-82.46, 35.31), "FREMANTLE, AU": (115.74, -32.05), "TILBURG, NL": (5.09, 51.55),
        "NAGOYA; AICHI, JP": (136.90, 35.18), "SANTO TOMAS DE CASTILLA, GT": (-88.61, 15.68),
        "SYDNEY, AU": (151.20, -33.86), "PEMULWUY, AU": (150.93, -33.82), "AMSTERDAM, NL": (4.90, 52.36),
        "OISTERWIJK, NL": (5.19, 51.58), "SINGAPORE, SG": (103.81, 1.35), "SAN ANTONIO, CL": (-71.61, -33.58),
        "PERTH, AU": (115.86, -31.95), "HUTHWAITE, GB": (-1.29, 53.13), "LAEM CHABANG, TH": (100.88, 13.08),
        "CAGAYAN DE ORO; MINDANAO, PH": (124.64, 8.47), "SAN JUAN, PR": (-66.10, 18.46), "TEMA, GH": (-0.01, 5.66),
        "BAR, ME": (19.10, 42.09), "BELGRADE, RS": (20.44, 44.81), "PUERTO CORTES, HN": (-87.93, 15.85),
        "EL PROGRESO, HN": (-87.80, 15.40), "KINGSTON, JM": (-76.79, 17.97), "IQUIQUE, CL": (-70.15, -20.21), 
        "IQUIQUE, TA": (-70.15, -20.21), "SANTO DOMINGO, DO": (-69.93, 18.48), "APODACA, MX": (-100.18, 25.78),
        "SHARJAH, AE": (55.41, 25.35), "DAR ES SALAAM, TZ": (39.26, -6.79), "BUJUMBURA, BI": (29.36, -3.38),
        "LONDON, GB": (-0.12, 51.50), "ENGLAND, AR": (-91.96, 34.54), "CARTERSVILLE, GA": (-84.79, 34.16), 
        "SAN NICOLAS DE LOS GARZA, MX": (-100.28, 25.74), "PUERTO LIMON, CR": (-83.03, 9.99), 
        "SAINT JOHN": (-66.06, 45.27), "TACOMA, WA": (-122.44, 47.25), "MANILA NORTH HARBOUR, PH": (120.96, 14.61), 
        "MANILA, PH": (120.98, 14.59), "HELSINKI, FI": (24.93, 60.16), "TURKU, FI": (22.26, 60.45),
        "MERSIN, TR": (34.64, 36.81), "BREMEN, DE": (8.80, 53.07), "ZAPOROZHYE, UA": (35.13, 47.83),
        "BELIZE CITY, BZ": (-88.19, 17.50), "CHORNOMORSK, UA": (30.65, 46.30), "DOBREJOVICE, CZ": (14.58, 49.98),
        "BEIRA, MZ": (34.83, -19.84), "DURRES, AL": (19.44, 41.32), "VALENCIA, ES": (-0.37, 39.46),
        "DOLYNKA": (0, 0), "LITTLE BAY, MS": (-88.1, 30.2), "MAYAGUEZ, PR": (-67.14, 18.20),
        "KHARKIV": (36.23, 50.00), "BRUSSELS, BELGIUM": (4.35, 50.85), "CHERNIGOV": (31.28, 51.49),
        "ADDIS ABABA, ET": (38.74, 9.03), "HO CHI MINH CITY, VN": (106.62, 10.82), "VINH LONG, VN": (105.96, 10.25),
        "MOIN, CR": (-83.02, 10.00), "ISLA VERDE, PR": (-66.01, 18.44), "MEXICO CITY, MX": (-99.13, 19.43),
        "HAMAD, QA": (51.59, 25.01), "DOHA, QA": (51.53, 25.28), "CHERNIGOV, UA": (31.28, 51.49),
        "POTI, GE": (41.67, 42.15), "KOSTANAY, KZ": (63.62, 53.21), "DJIBOUTI, DJ": (43.14, 11.58),
        "JEDDAH, SA": (39.19, 21.48), "LA HABANA, CU": (-82.36, 23.11), "MARIEL, CU": (-82.75, 22.99),
        "CORINTO, NI": (-87.17, 12.48), "ESTELI, NI": (-86.35, 13.09), "DAMMAM, SA": (50.10, 26.42),
        "SZCZECIN, PL": (14.55, 53.42), "NIKOLAEV, UA": (31.99, 46.97), "ODESSA, UA": (30.73, 46.48),
        "ZOLOTONOSHA, UA": (32.03, 49.66), "NGOZI, BI": (29.82, -2.90), "KWINANA, AU": (115.77, -32.24), 
        "HAMILTON, MS": (-88.4, 33.8), "BRIDGETOWN, BB": (-59.61, 13.09), "LAREDO, TX": (-99.50, 27.50), 
        "NUEVO LAREDO, MX": (-99.50, 27.47), "MOMBASA, KE": (39.66, -4.04), "NAIROBI, KE": (36.82, -1.29),
        "MONROVIA, LR": (-10.79, 6.31), "ZARATE, AR": (-59.02, -34.09), "FREEPORT, TX": (-95.35, 28.94),
        "BUENOS AIRES, AR": (-58.38, -34.60), "LA SALINE LES HAUTS, RE": (55.26, -21.09),
        "LAGOS, NG": (3.37, 6.52), "TINCAN/LAGOS, NG": (3.37, 6.52), "MUNDRA, IN": (69.71, 22.84),
        "NEW YORK, GB": (-1.4, 54.0), "VIGO, ES": (-8.72, 42.24), "DUBAI, AE": (55.27, 25.20),
        "SEATTLE, WA": (-122.33, 47.60), "XIAMEN, CN": (118.08, 24.47), "VANCOUVER, BC": (-123.12, 49.28),
        "AUGUSTA, GA": (-81.97, 33.47), "WATERLOO, ON": (-80.52, 43.46), "BALTIMORE, MD": (-76.61, 39.29),
        "ORANGE, VA": (-78.11, 38.24), "ESCOBEDO, MX": (-100.32, 25.80), "TULSA, OK": (-95.99, 36.15),
        "ALBUQUERQUE, NM": (-106.65, 35.08), "MEMPHIS, TN": (-90.04, 35.14), "LEICESTER, MA": (-71.90, 42.24),
        "BOSTON, MA": (-71.05, 42.36), "TAIPEI, TW": (121.56, 25.03), "FRANKFURT AM MAIN, DE": (8.68, 50.11),
        "DANVILLE, IN": (-86.52, 39.76), "MAINE": (-69.06, 45.36), "AUSTRAL DOWNS, AU": (137.95, -20.67),
        "CORONA, CA": (-117.56, 33.87), "SPARTANBURG, SC": (-81.93, 34.94), "CARPINTERIA, CA": (-119.51, 34.39),
        "PICKERING, CA": (-79.08, 43.83), "ORLANDO, FL": (-81.37, 28.53), "QINZHOU, CN": (108.62, 21.95),
        "BELAWAN; SUMATRA, ID": (98.68, 3.78), "GORMLEY, ON": (-79.38, 43.93), "ETOBICOKE, CA": (-79.57, 43.62),
        "LAVAL, CA": (-73.75, 45.60), "SPRUCE GROVE, CA": (-113.90, 53.54), "CALGARY, CA": (-114.07, 51.04),
        "YANGON, MM": (96.15, 16.84), "FLINT, MI": (-83.68, 43.01), "BLUE RIDGE, GA": (-84.32, 34.86),
        "HIALEAH, FL": (-80.27, 25.85), "KEY BISCAYNE, FL": (-80.16, 25.69), "LA VERGNE, TN": (-86.58, 36.01),
        "RICHMOND, VA": (-77.43, 37.54), "PRINCE RUPERT, CA": (-130.32, 54.31), "CHARLOTTE, NC": (-80.84, 35.22),
        "HIGH POINT, NC": (-80.00, 35.95), "MORIARTY, NM": (-106.04, 35.00), "EDMONTON, CA": (-113.49, 53.54),
        "PERRIS, CA": (-117.22, 33.78), "MIDDLE ISLAND, NY": (-72.94, 40.88), "LINTHICUM HEIGHTS, MD": (-76.65, 39.20),
        "LEGHORN | LIVORNO": (10.31, 43.54), "HAZIRA, IN": (72.63, 21.11),
        "NEW CITY, NY": (-73.99, 41.14), "PASADENA, TX": (-95.20, 29.69), "ALIAGA, TR": (26.97, 38.79),
        "PULASKI, VA": (-80.78, 37.04), "CAIRO, GA": (-84.20, 30.87), "CAMPHILL, PA": (-76.92, 40.24),
        "TUCKER, GA": (-84.22, 33.85), "EAST WENATCHEE, WA": (-120.29, 47.41), "ARLINGTON, TX": (-97.10, 32.73),
        "CAMBY, IN": (-86.32, 39.63), "NEW DUNDEE, ON": (-80.55, 43.37), "CHERRY HILL, NJ": (-75.03, 39.93),
        "LIVORNO, IT": (10.31, 43.54), "DES MOINES, IA": (-93.60, 41.58), "ELGIN, IL": (-88.28, 42.03),
        "GRAND RAPIDS, MI": (-85.66, 42.96), "PARIS, FR": (2.35, 48.85), "TRENTON, CA": (-77.58, 44.10),
        "JESSUP, MD": (-76.77, 39.14), "SEAGERTOWN, PA": (-80.14, 41.71), "OXFORD, AL": (-85.83, 33.61),
        "WAUWATOSA, WI": (-88.00, 43.04), "WATERLOO, CA": (-80.52, 43.46), "AUSTIN, TX": (-97.74, 30.26),
        "BRIDGEVIEW, IL": (-87.80, 41.75), "TUCAPEL": (-71.93, -37.28), "LA SPEZIA, IT": (9.82, 44.10),
        "SAINT GEORGE, UT": (-113.58, 37.09), "WATCHUNG, NJ": (-74.43, 40.63), "MILANO, IT": (9.18, 45.46),
        "NORTH HIGHLANDS, CA": (-121.37, 38.67), "VUNG TAU, VN": (107.08, 10.34), "EAGLE MOUNTAIN, UT": (-112.00, 40.31),
        "CLINTON TOWNSHIP, MI": (-82.91, 42.58), "NEPHI, UT": (-111.83, 39.70), "BRUNSWICK, GA": (-81.49, 31.14),
        "LUBBOCK, TX": (-101.85, 33.57), "FUZHOU, CN": (119.29, 26.07), "SCARBOROUGH, ME": (-70.32, 43.57),
        "POWELL, WY": (-108.75, 44.75), "MOORESVILLE, NC": (-80.81, 35.58), "MORRICE,MI": (-84.18, 42.83),
        "CELINA, TX": (-96.78, 33.32), "ALANSON, MI": (-84.78, 45.44), "HEBER CITY, UT": (-111.41, 40.50),
        "VAIL, CO": (-106.37, 39.64), "GRIFFIN, GA": (-84.26, 33.24), "INVERMERE, CA": (-116.03, 50.50),
        "SOUTH BOSTON, VA": (-78.90, 36.69), "RUTLAND, VT": (-72.97, 43.61), "ASHTABULA, OH": (-80.79, 41.86),
        "BENNETT, CO": (-104.42, 39.75), "INDIANTOWN, FL": (-80.47, 27.03), "KANSAS CITY, MO": (-94.57, 39.09),
        "LUXEMBOURG, LU": (6.13, 49.61), "HAMPTON, GA": (-84.28, 33.38), "QUEENS/NEW YORK, NY": (-73.82, 40.72),
        "PURDY, MO": (-93.92, 36.81), "BALTIMORE, MD": (-76.61, 39.29), "ENNORE, IN": (80.32, 13.26),
        "SHANGHAI PU DONG APT, CN": (121.80, 31.14), "POINT ROBERTS, WA": (-123.06, 48.98),
        "HOBE SOUND, FL": (-80.13, 27.05), "SAN MARCOS, CA": (-117.16, 33.14), "PENSACOLA, FL": (-87.21, 30.42),
        "INCHEON, KR": (126.70, 37.45), "BROWNSVILLE, TX": (-97.49, 25.90), "EL PASO, TX": (-106.48, 31.76),
        "HIDALGO, TX": (-98.26, 26.10), "SANTA TERESA, NM": (-106.68, 31.86), "SANTA TERESA, MX": (-106.68, 31.86), 
        "NOGALES, AZ": (-110.93, 31.33), "ELIZABETHTOWN, KY": (-85.85, 37.69), "BELLEVUE, OH": (-82.84, 41.27),
        "GOMEZ PALACIO, MX": (-103.49, 25.56), "GLASGOW, KY": (-85.91, 37.00), "QUERETARO, MX": (-100.38, 20.58),
        "JESUP, GA": (-81.88, 31.60), "MEDLEY, FL": (-80.32, 25.84), "PARIS, TX": (-95.55, 33.66),
        "BATON ROUGE, LA": (-91.14, 30.45), "BEIJING, CN": (116.40, 39.90), "SAO PAULO, BR": (-46.63, -23.55),
        "NEW DELHI, IN": (77.20, 28.61), "SAINT ROSE PLANTATION, LA": (-90.31, 29.95), "LEBANON, OR": (-122.90, 44.53),
        "PELZER, SC": (-82.46, 34.64), "HARLAN, IA": (-95.32, 41.65), "MOUNT VERNON, WA": (-122.33, 48.42),
        "CUAUTITLAN IZCALLI, MX": (-99.21, 19.64), "LAZARO CARDENAS, MX": (-102.19, 17.95), "TIANJIN, CN": (117.20, 39.08),
        "PROGRESO, MX": (-89.66, 21.28), "CANYON COUNTRY, CA": (-118.45, 34.42), "MIRA LOMA, CA": (-117.51, 33.98),
        "MACON, GA": (-84.16, 32.84), "OSTEEN, FL": (-81.15, 28.84), "SPOKANE, WA": (-117.42, 47.65),
        "TRUCKEE, CA": (-120.18, 39.32), "WEST CHESTER TOWNSHIP, OH": (-84.40, 39.33),
        "ATLANTA REGIONAL AIRPORT - FALCON FIELD": (-84.56, 33.35), "FORT LAUDERDALE, FL": (-80.14, 26.12),
        "PULASKI, TN": (-87.03, 35.20), "CAROLINA SHORES, NC": (-78.58, 33.88), "MCHENRY, IL": (-88.26, 42.33),
        "WINSLOW, AZ": (-110.69, 35.02), "SCOTTSBLUFF, NE": (-103.66, 41.86), "GARY, IN": (-87.34, 41.59),
        "CHICOPEE, MA": (-72.58, 42.14), "LAT KRABANG, TH": (100.78, 13.72), "MICHIGAN CITY, IN": (-86.89, 41.71),
        "CLEVELAND, OH": (-81.69, 41.49), "CALHOUN, GA": (-84.95, 34.50), "VILLAS, NC": (0,0), 
        "VON ORMY, TX": (-98.64, 29.28), "WOLCOTT, IN": (-87.04, 40.75), "TRENTON, ON": (-77.58, 44.10),
        "NEW CANAAN, CT": (-73.49, 41.14), "KATTUPALLI PORT, INDIA": (80.32, 13.31), "CHITTAGONG, BD": (91.78, 22.35),
        "NEWPORT, GB": (-2.99, 51.58), "HUNTINGBURG, IN": (-86.95, 38.29), "CAGUAS, PR": (-66.04, 18.23),
        "COOLIDGE, AZ": (-111.52, 32.97), "WASHINGTON, DC": (-77.03, 38.90), "INDIO, CA": (-116.21, 33.72),
        "TULSA, OK": (-95.99, 36.15), "NEGAUNEE, MI": (-87.60, 46.50), "STOYSTOWN, PA": (-78.95, 40.10),
        "MCDONOUGH, GA": (-84.14, 33.44), "SUVARNABHUMI INTL": (100.75, 13.68), "HARTSFIELD JACKSON ATLANTA INTL": (-84.42, 33.64),
        "ALPHARETTA, GA": (-84.29, 34.07), "HONG KONG, HK": (114.16, 22.31), "STATESVILLE, NC": (-80.88, 35.78),
        "CHENNAI, IN": (80.27, 13.08), "CHARLOTTE DOUGLAS INTL": (-80.94, 35.21), "TANSONNHAT INTL": (106.66, 10.81),
        "NOIBAI INTL": (105.80, 21.22), "WILMER, TX": (-96.68, 32.59), "DALLAS FORT WORTH INTL, USA": (-97.04, 32.89),
        "DALLAS FORT WORTH INTL, US": (-97.04, 32.89), "DALLAS-FORT WORTH INT APT, TX": (-97.04, 32.89),
        "CAMP HILL, PA": (-76.92, 40.24), "NEWARK LIBERTY INTL": (-74.17, 40.69), "YORK, PA": (-76.72, 39.96),
        "CHAGRIN FALLS, OH": (-81.39, 41.42), "HAMBURG, DE": (9.99, 53.55), "CLEVELAND HOPKINS INTL": (-81.84, 41.41),
        "GEORGETOWN, TN": (-84.89, 35.29), "AMSTERDAM, NL": (4.90, 52.36), "SPRINGFIELD, MO": (-93.29, 37.20),
        "TAOYUAN, TW": (121.30, 24.99), "KANSAS CITY INTL": (-94.71, 39.29), "MANHATTAN/NEW YORK, NY": (-74.00, 40.71),
        "MILANO, IT": (9.18, 45.46), "JANESVILLE, WI": (-89.01, 42.68), "VIENNA | WIEN": (16.37, 48.20),
        "CHICAGO OHARE INTL": (-87.90, 41.97), "SHANGHAI, CN": (121.47, 31.23), "FRANKFURT ODER HBF": (14.54, 52.34),
        "FRANKFURT MAIN": (8.57, 50.03), "JOHN F KENNEDY INTL": (-73.77, 40.64), "JOHN F. KENNEDY APT/NEW YORK, NY": (-73.77, 40.64),
        "NEW YORK, NY": (-74.00, 40.71), "CHANDLER, AZ": (-111.83, 33.30), "PHOENIX SKY HARBOR INTL": (-112.00, 33.43),
        "DELHI, IN": (77.10, 28.70), "NEW DELHI, IN": (77.20, 28.61), "BARCELONA": (2.17, 41.38),
        "PHILADELPHIA INTL": (-75.24, 39.87), "DULLES INT APT/WASHINGTON, VA": (-77.45, 38.95), "DULLES, VA": (-77.45, 38.95),
        "PARK RIDGE, NJ": (-74.03, 41.03), "MILAN | MILANO": (9.18, 45.46), "NEW HOLLAND, PA": (-76.08, 40.10),
        "OSLO, NO": (10.75, 59.91), "INDIANAPOLIS, IN": (-86.15, 39.76), "JACKSONVILLE, FL": (-81.65, 30.33),
        "JOHANNESBURG INTL": (28.24, -26.13), "PERTH, AU": (115.86, -31.95), "DENVER INTLAPT": (-104.67, 39.86),
        "EAST LIBERTY, OH": (-83.58, 40.30), "MADRID, ES": (-3.70, 40.41), "CINCINNATI NORTHERN KENTUCKY INTL": (-84.66, 39.05),
        "DIXON, IL": (-89.48, 41.84), "THOMASVILLE, GA": (-83.97, 30.83), "TRACY, CA": (-121.42, 37.73),
        "SHENZHEN, CN": (114.05, 22.54), "SAN FRANCISCO INTL, US": (-122.37, 37.61), "O'HARE APT/CHICAGO, IL": (-87.90, 41.97),
        "BEIJING, CN": (116.40, 39.90), "NEWARK APT/NEW YORK, NJ": (-74.17, 40.69), "NEWARK, NJ": (-74.17, 40.73),
        "MINNEAPOLIS/ST PAUL APT, MN": (-93.22, 44.88), "DUBAI, AE": (55.27, 25.20), "SARAJEVO, BA": (18.41, 43.85),
        "SURABAYA, ID": (112.75, -7.25), "LONG BEACH, CA": (-118.19, 33.77), "WUHAN, CN": (114.29, 30.59),
        "SAVANNAH, GA": (-81.09, 32.08), "SECAUCUS, NJ": (-74.05, 40.78), "PHOENIX, AZ": (-112.07, 33.44),
        "MANILA, PH": (120.98, 14.59), "SALT LAKE CITY, UT": (-111.89, 40.76), "MOORESTOWN, NJ": (-74.94, 39.96),
        "HEATHROW APT/LONDON, GB": (-0.45, 51.47), "TOCUMEN INTL": (-79.38, 9.07), "MIAMI, FL": (-80.19, 25.76),
        "BROOKLYN/NEW YORK, NY": (-73.94, 40.67), "MALPENSA APT/MILANO, IT": (8.72, 45.63), "EULESS, TX": (-97.08, 32.83),
        "CAI MEP, VN": (107.03, 10.53), "LOS ANGELES, CA": (-118.24, 34.05), "HO CHI MINH CITY, VN": (106.62, 10.82),
        "GEORGE BUSH INTERCONTINENTAL, US": (-95.33, 29.99), "NINOY AQUINO INTL": (121.01, 14.50), "KAMUZU INTL": (33.78, -13.78),
        "SIR SERETSE KHAMA INTL": (25.92, -24.55), "VILNIUS INTL": (25.28, 54.63), "KILIMANJARO INTL": (37.07, -3.42),
        "ARUSHA, TZ": (36.68, -3.36), "GABORONE, BW": (25.92, -24.62), "LOS ANGELES INTL, US": (-118.40, 33.94),
        "CADIZ, ES": (-6.29, 36.53), "ROME | ROMA": (12.49, 41.90), "ADDIS ABABA, ET": (38.74, 9.03),
        "WINDHOEK HOSEA KUTAKO INTERNATIONAL AIRPORT": (17.46, -22.48), "ATL/SJU/1109959": (-66.10, 18.46),
        "SAN JUAN, PR": (-66.10, 18.46), "ANCONA, IT": (13.51, 43.61), "PITTSBURGH INTERNATIONAL AIRPORT": (-80.23, 40.49),
        "MANCHESTER AIRPORT": (-2.27, 53.35), "HEANOR, GB": (-1.35, 53.01), "ATL/SJU/1152528": (-66.10, 18.46),
        "PHILADELPHIA, PA": (-75.16, 39.95), "N'DJAMENA, TD": (15.05, 12.13), "JOHANNESBURG, ZA": (28.04, -26.20),
        "SAN FRANCISCO, CA": (-122.41, 37.77), "MIAMI INTL, US": (-80.28, 25.79), "MAYAGUEZ, PR": (-67.14, 18.20),
        "LAREDO, TX": (-99.50, 27.50), "NUEVO LAREDO, MX": (-99.50, 27.47), "TLAQUEPAQUE, MX": (-103.31, 20.64),
        "ZURICH, CH": (8.54, 47.37), "BURGDORF, CH": (7.62, 47.05), "JORDAN, IL": (-88.13, 42.20),
        "IQUIQUE, CL": (-70.15, -20.21), "ATHENS, GR": (23.72, 37.98), "PERRYVILLE, MD": (-76.06, 39.56),
        "BALTIMORE-WASHINGTON INT APT, MD": (-76.66, 39.17), "GRAYSLAKE, IL": (-88.04, 42.34),
        "GORMLEY, CA": (-118.19, 33.77), "GORMLEY, ON": (-79.38, 43.93)
    }

coords_cache = get_coords_cache()
geolocator = Nominatim(user_agent="logistics_carbon_calculator")

def get_coordinates(loc_str):
    if pd.isna(loc_str): return None
    loc_str = str(loc_str).strip().upper()
    if loc_str in coords_cache: return coords_cache[loc_str]
    try:
        loc = geolocator.geocode(loc_str, timeout=5)
        if loc:
            coords_cache[loc_str] = (loc.longitude, loc.latitude)
            return (loc.longitude, loc.latitude)
    except: pass
    coords_cache[loc_str] = None
    return None

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 3956

def calculate_distance(loc1, loc2):
    if loc1 == loc2: return 10.0
    c1, c2 = get_coordinates(loc1), get_coordinates(loc2)
    if c1 and c2: return haversine(c1[0], c1[1], c2[0], c2[1])
    return 100.0

def find_header_row(df):
    for i in range(min(5, len(df))):
        if 'FILE_NUMBER' in df.iloc[i].values or 'POL' in df.iloc[i].values:
            return i + 1
    return 0

# --- 2. USER INTERFACE ---
uploaded_files = st.file_uploader("Upload your CSV files (Drag & Drop all at once)", type=['csv'], accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 Calculate Emissions"):
        with st.spinner('Calculating distances and emissions... this may take a minute.'):
            
            unrealistic_files = [f for f in uploaded_files if "Unrealistic" in f.name]
            data_files = [f for f in uploaded_files if "Unrealistic" not in f.name]
            
            excluded_file_numbers = set()
            for uf in unrealistic_files:
                udf = pd.read_csv(uf, header=None)
                header_idx = find_header_row(udf)
                udf = pd.read_csv(uf, skiprows=header_idx)
                if 'FILE_NUMBER' in udf.columns:
                    excluded_file_numbers.update(udf['FILE_NUMBER'].astype(str).str.replace(r'\.0$', '', regex=True))
            
            master_data = []
            
            for file in data_files:
                fname_upper = file.name.upper()
                export_import = "Export" if "EXPORT" in fname_upper else "Import" if "IMPORT" in fname_upper else "N/A"
                container_type = "FCL" if "FCL" in fname_upper else "LCL" if "LCL" in fname_upper else "N/A"
                
                if "FLIGHTS" in fname_upper: shipment_type = "Air"
                elif "TRUCK" in fname_upper: shipment_type = "Trucks"
                else: shipment_type = "Ocean"
                
                p = PARAMS[shipment_type]
                df_raw = pd.read_csv(file, header=None)
                df = pd.read_csv(file, skiprows=find_header_row(df_raw))
                
                for _, row in df.iterrows():
                    file_num = str(row.get('FILE_NUMBER', '')).replace('.0', '')
                    if not file_num or str(file_num).lower() == 'nan' or file_num in excluded_file_numbers: 
                        continue
                        
                    pol = str(row.get('POL', '')).strip()
                    pod = str(row.get('POD', '')).strip()
                    dest = str(row.get('DESTINATION', '')).strip()
                    if dest.lower() == 'nan': dest = ''
                    
                    dist1 = calculate_distance(pol, pod)
                    dist2 = calculate_distance(pod, dest) if dest and dest != pod else 0
                    total_dist = dist1 + dist2
                    
                    route_str = f"{pol} ➔ {pod}" + (f" ➔ {dest}" if dest and dest != pod else "")
                    
                    count = 1
                    if 'NO_OF_CONTAINERS' in row and pd.notna(row['NO_OF_CONTAINERS']):
                        try: count = float(row['NO_OF_CONTAINERS'])
                        except: pass
                            
                    co2e = count * p['weight'] * (total_dist * p['multiplier']) * p['factor']
                    
                    master_data.append({
                        'Routes': route_str, 'Number of Containers': count, 'File Numbers': file_num,
                        'Route Distance (mi)': total_dist, 'Export or Import': export_import,
                        'Container Type': container_type, 'Shipment Type': shipment_type, 'Total Route CO2e': co2e
                    })

            if master_data:
                df_master = pd.DataFrame(master_data)
                final_df = df_master.groupby(
                    ['Routes', 'Export or Import', 'Container Type', 'Shipment Type', 'Route Distance (mi)']
                ).agg({
                    'Number of Containers': 'sum',
                    'File Numbers': lambda x: ', '.join(x.unique()),
                    'Total Route CO2e': 'sum'
                }).reset_index()

                final_df['Route Distance (mi)'] = final_df['Route Distance (mi)'].round(1)
                final_df['Total Route CO2e'] = final_df['Total Route CO2e'].round(0)
                final_df = final_df.sort_values(by='Total Route CO2e', ascending=False)
                
                total_lbs = final_df['Total Route CO2e'].sum()
                total_mt = total_lbs / 2204.62
                
                st.success("✅ Calculation Complete!")
                col1, col2 = st.columns(2)
                col1.metric("Total CO₂e (lbs)", f"{total_lbs:,.0f} lbs")
                col2.metric("Total CO₂e (Metric Tons)", f"{total_mt:,.2f} MT")
                
                st.subheader("Route Breakdown")
                st.dataframe(final_df)
                
                csv = final_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Full Report (CSV)",
                    data=csv,
                    file_name='Consolidated_Global_Carbon_Footprint.csv',
                    mime='text/csv',
                )
              
