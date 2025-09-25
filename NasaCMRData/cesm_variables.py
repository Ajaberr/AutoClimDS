# CESM Variable Standards Reference
# Auto-generated from CESM2 Large Ensemble Community Project (LENS2)
# Source: https://www.cesm.ucar.edu/community-projects/lens2/output-variables
# Generated on: 2025-06-24 09:00:46

# CESM Components (7 total)
CESM_COMPONENTS = {
    "atm": {
        "full_name": "Community Atmosphere Model",
        "abbreviation": "CAM",
        "description": "Atmospheric component of CESM - handles  atmospheric dynamics, physics, and chemistry",
        "domain": "atmosphere"
    },
    "ocn": {
        "full_name": "Parallel Ocean Program",
        "abbreviation": "POP",
        "description": "Ocean component of CESM - simulates ocean circulation, temperature, and biogeochemistry",
        "domain": "ocean"
    },
    "lnd": {
        "full_name": "Community Land Model",
        "abbreviation": "CLM",
        "description": "Land component of CESM - models land surface processes, vegetation, and biogeochemistry",
        "domain": "land"
    },
    "ice": {
        "full_name": "Community Ice CodE",
        "abbreviation": "CICE",
        "description": "Sea ice component of CESM - simulates sea ice dynamics and thermodynamics",
        "domain": "seaice"
    },
    "rof": {
        "full_name": "Model for Scale Adaptive River Transport",
        "abbreviation": "MOSART",
        "description": "River routing component of CESM - handles river discharge and routing",
        "domain": "land"
    },
    "glc": {
        "full_name": "Community Ice Sheet Model",
        "abbreviation": "CISM",
        "description": "Glacier/ice sheet component of CESM - models ice sheet dynamics",
        "domain": "ice"
    },
    "wav": {
        "full_name": "WaveWatch III",
        "abbreviation": "WW3",
        "description": "Wave component of CESM - simulates ocean surface waves",
        "domain": "ocean"
    }
}

# CESM Variables (1981 total)
CESM_VARIABLES = {
    "CLDICE": {
        "standard_name": "mass_fraction_of_cloud_ice_in_air",
        "cesm_name": "CLDICE",
        "units": "kg/kg",
        "description": "Grid box averaged cloud ice amount",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDLIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "CLDLIQ",
        "units": "kg/kg",
        "description": "Grid box averaged cloud liquid amount",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLOUD": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLOUD",
        "units": "fraction",
        "description": "Cloud fraction",
        "domain": "atmosphere",
        "component": "std"
    },
    "CMFMCDZM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CMFMCDZM",
        "units": "kg/m2/s",
        "description": "Convection mass flux from ZM deep",
        "domain": "atmosphere",
        "component": "std"
    },
    "CMFMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CMFMC",
        "units": "kg/m2/s",
        "description": "Moist convection (deep+shallow) mass flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DCQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "DCQ",
        "units": "kg/kg/s",
        "description": "Q tendency due to moist processes",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DTCOND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DTCOND",
        "units": "K/s",
        "description": "T tendency - moist processes",
        "domain": "atmosphere",
        "component": "std"
    },
    "DTV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DTV",
        "units": "K/s",
        "description": "T vertical diffusion",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNTOA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNTOA",
        "units": "W/m2",
        "description": "Net solar flux at top of atmosphere",
        "domain": "atmosphere",
        "component": "std"
    },
    "MASS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MASS",
        "units": "kg",
        "description": "mass of grid box",
        "domain": "atmosphere",
        "component": "std"
    },
    "OMEGA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "OMEGA",
        "units": "Pa/s",
        "description": "Vertical velocity (pressure)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PDELDRY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PDELDRY",
        "units": "Pa",
        "description": "Dry pressure difference between levels",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRL": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRL",
        "units": "K/s",
        "description": "Longwave heating rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRS": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRS",
        "units": "K/s",
        "description": "Solar heating rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNOW": {
        "standard_name": "snowfall_flux",
        "cesm_name": "QSNOW",
        "units": "kg/kg",
        "description": "Diagnostic grid-mean snow mixing ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "Q": {
        "standard_name": "specific_humidity",
        "cesm_name": "Q",
        "units": "gram/centimeter^4",
        "description": "Static Stability (d(rho(p_r))/dz)",
        "domain": "atmosphere",
        "component": "std"
    },
    "RELHUM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RELHUM",
        "units": "percent",
        "description": "Relative humidity",
        "domain": "atmosphere",
        "component": "std"
    },
    "THzm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "THzm",
        "units": "K",
        "description": "Zonal-Mean potential temp - defined on ilev",
        "domain": "atmosphere",
        "component": "std"
    },
    "T": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "T",
        "units": "K",
        "description": "Temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "U": {
        "standard_name": "eastward_wind",
        "cesm_name": "U",
        "units": "m/s",
        "description": "Zonal wind",
        "domain": "atmosphere",
        "component": "std"
    },
    "UTGWORO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UTGWORO",
        "units": "m/s2",
        "description": "U tendency - orographic gravity wave drag",
        "domain": "atmosphere",
        "component": "std"
    },
    "UVzm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UVzm",
        "units": "M2/S2",
        "description": "Meridional Flux of Zonal Momentum: 3D zon. mean",
        "domain": "atmosphere",
        "component": "std"
    },
    "UWzm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UWzm",
        "units": "M2/S2",
        "description": "Vertical Flux of Zonal Momentum: 3D zon. mean",
        "domain": "atmosphere",
        "component": "std"
    },
    "Uzm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Uzm",
        "units": "M/S",
        "description": "Zonal-Mean zonal wind - defined on ilev",
        "domain": "atmosphere",
        "component": "std"
    },
    "V": {
        "standard_name": "northward_wind",
        "cesm_name": "V",
        "units": "m/s",
        "description": "Meridional wind",
        "domain": "atmosphere",
        "component": "std"
    },
    "VTHzm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VTHzm",
        "units": "MK/S",
        "description": "Meridional Heat Flux: 3D zon. mean",
        "domain": "atmosphere",
        "component": "std"
    },
    "Vzm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Vzm",
        "units": "M/S",
        "description": "Zonal-Mean meridional wind - defined on ilev",
        "domain": "atmosphere",
        "component": "std"
    },
    "Wzm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Wzm",
        "units": "M/S",
        "description": "Zonal-Mean vertical wind - defined on ilev",
        "domain": "atmosphere",
        "component": "std"
    },
    "Z3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Z3",
        "units": "m",
        "description": "Geopotential Height (above sea level)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PRECT": {
        "standard_name": "precipitation_flux",
        "cesm_name": "PRECT",
        "units": "m/s",
        "description": "Total (convective and large-scale) precipitation rate (liq+ice)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CLDLOW": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDLOW",
        "units": "fraction",
        "description": "Vertically-integrated low cloud",
        "domain": "atmosphere",
        "component": "std"
    },
    "CLDTOT": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDTOT",
        "units": "fraction",
        "description": "Vertically-integrated total cloud",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLUT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLUT",
        "units": "W/m2",
        "description": "Upwelling longwave flux at top of model",
        "domain": "atmosphere",
        "component": "std"
    },
    "LHFLX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LHFLX",
        "units": "W/m2",
        "description": "Surface latent heat flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "PRECC": {
        "standard_name": "precipitation_flux",
        "cesm_name": "PRECC",
        "units": "m/s",
        "description": "Convective precipitation rate (liq+ice)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PRECL": {
        "standard_name": "precipitation_flux",
        "cesm_name": "PRECL",
        "units": "m/s",
        "description": "Large-scale (stable) precipitation rate (liq+ice)",
        "domain": "atmosphere",
        "component": "std"
    },
    "UBOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UBOT",
        "units": "m/s",
        "description": "Lowest model level zonal wind",
        "domain": "atmosphere",
        "component": "std"
    },
    "VBOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VBOT",
        "units": "m/s",
        "description": "Lowest model level meridional wind",
        "domain": "atmosphere",
        "component": "std"
    },
    "IVT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "IVT",
        "units": "kg m-2 s-1",
        "description": "Integrated Vapor Transport",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PS": {
        "standard_name": "surface_air_pressure",
        "cesm_name": "PS",
        "units": "Pa",
        "description": "Surface pressure",
        "domain": "atmosphere",
        "component": "std"
    },
    "QREFHT": {
        "standard_name": "specific_humidity",
        "cesm_name": "QREFHT",
        "units": "kg/kg",
        "description": "Reference height humidity",
        "domain": "atmosphere",
        "component": "std"
    },
    "TMQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "TMQ",
        "units": "kg/m2",
        "description": "Total (vertically integrated) precipitable water",
        "domain": "atmosphere",
        "component": "std"
    },
    "TS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TS",
        "units": "K",
        "description": "Surface temperature (radiative)",
        "domain": "atmosphere",
        "component": "std"
    },
    "uIVT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "uIVT",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "moar"
    },
    "vIVT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "vIVT",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "moar"
    },
    "bc_a1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a1DDF",
        "units": "kg/m2/s",
        "description": "bc_a1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "bc_a1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a1SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "bc_c1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_c1DDF",
        "units": "kg/m2/s",
        "description": "bc_c1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "bc_c1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_c1SFWET",
        "units": "kg/m2/s",
        "description": "bc_c1 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "bc_c1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_c1",
        "units": "kg/kg",
        "description": "bc_c1 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CFAD_DBZE94_CS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CFAD_DBZE94_CS",
        "units": "fraction",
        "description": "Radar Reflectivity Factor CFAD (94 GHz)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CFAD_SR532_CAL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CFAD_SR532_CAL",
        "units": "fraction",
        "description": "Lidar Scattering Ratio CFAD (532 nm)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLD_CAL_ICE": {
        "standard_name": "mass_fraction_of_cloud_ice_in_air",
        "cesm_name": "CLD_CAL_ICE",
        "units": "percent",
        "description": "Lidar Ice Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLD_CAL_LIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "CLD_CAL_LIQ",
        "units": "percent",
        "description": "Lidar Liquid Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLD_CAL_NOTCS": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLD_CAL_NOTCS",
        "units": "percent",
        "description": "Cloud occurrence seen by CALIPSO but not CloudSat",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLD_CAL": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLD_CAL",
        "units": "percent",
        "description": "Lidar Cloud Fraction (532 nm)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLD_CAL_UN": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLD_CAL_UN",
        "units": "percent",
        "description": "Lidar Undefined-Phase Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDHGH_CAL_ICE": {
        "standard_name": "mass_fraction_of_cloud_ice_in_air",
        "cesm_name": "CLDHGH_CAL_ICE",
        "units": "percent",
        "description": "Lidar High-level Ice Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDHGH_CAL_LIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "CLDHGH_CAL_LIQ",
        "units": "percent",
        "description": "Lidar High-level Liquid Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDHGH_CAL": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDHGH_CAL",
        "units": "percent",
        "description": "Lidar High-level Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDHGH_CAL_UN": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDHGH_CAL_UN",
        "units": "percent",
        "description": "Lidar High-level Undefined-Phase Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDLOW_CAL_ICE": {
        "standard_name": "mass_fraction_of_cloud_ice_in_air",
        "cesm_name": "CLDLOW_CAL_ICE",
        "units": "percent",
        "description": "Lidar Low-level Ice Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDLOW_CAL_LIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "CLDLOW_CAL_LIQ",
        "units": "percent",
        "description": "Lidar Low-level Liquid Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDLOW_CAL": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDLOW_CAL",
        "units": "percent",
        "description": "Lidar Low-level Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDLOW_CAL_UN": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDLOW_CAL_UN",
        "units": "percent",
        "description": "Lidar Low-level Undefined-Phase Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDMED_CAL_ICE": {
        "standard_name": "mass_fraction_of_cloud_ice_in_air",
        "cesm_name": "CLDMED_CAL_ICE",
        "units": "percent",
        "description": "Lidar Mid-level Ice Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDMED_CAL_LIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "CLDMED_CAL_LIQ",
        "units": "percent",
        "description": "Lidar Mid-level Liquid Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDMED_CAL": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDMED_CAL",
        "units": "percent",
        "description": "Lidar Mid-level Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDMED_CAL_UN": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDMED_CAL_UN",
        "units": "percent",
        "description": "Lidar Mid-level Undefined-Phase Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLD_MISR": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLD_MISR",
        "units": "percent",
        "description": "Cloud Fraction from MISR Simulator",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDTOT_CALCS": {
        "standard_name": "air_temperature",
        "cesm_name": "CLDTOT_CALCS",
        "units": "percent",
        "description": "Lidar and Radar Total Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDTOT_CAL_ICE": {
        "standard_name": "air_temperature",
        "cesm_name": "CLDTOT_CAL_ICE",
        "units": "percent",
        "description": "Lidar Total Ice Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDTOT_CAL_LIQ": {
        "standard_name": "air_temperature",
        "cesm_name": "CLDTOT_CAL_LIQ",
        "units": "percent",
        "description": "Lidar Total Liquid Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDTOT_CAL": {
        "standard_name": "air_temperature",
        "cesm_name": "CLDTOT_CAL",
        "units": "percent",
        "description": "Lidar Total Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDTOT_CAL_UN": {
        "standard_name": "air_temperature",
        "cesm_name": "CLDTOT_CAL_UN",
        "units": "percent",
        "description": "Lidar Total Undefined-Phase Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDTOT_CS2": {
        "standard_name": "air_temperature",
        "cesm_name": "CLDTOT_CS2",
        "units": "percent",
        "description": "Radar total cloud amount without the data for the first kilometer above surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDTOT_CS": {
        "standard_name": "air_temperature",
        "cesm_name": "CLDTOT_CS",
        "units": "percent",
        "description": "Radar total cloud amount",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLDTOT_ISCCP": {
        "standard_name": "air_temperature",
        "cesm_name": "CLDTOT_ISCCP",
        "units": "percent",
        "description": "Total Cloud Fraction Calculated by the ISCCP Simulator",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLHMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLHMODIS",
        "units": "%",
        "description": "MODIS High Level Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLIMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLIMODIS",
        "units": "%",
        "description": "MODIS Ice Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLLMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLLMODIS",
        "units": "%",
        "description": "MODIS Low Level Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLMMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLMMODIS",
        "units": "%",
        "description": "MODIS Mid Level Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLMODIS",
        "units": "%",
        "description": "MODIS Cloud Area Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLRIMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLRIMODIS",
        "units": "%",
        "description": "MODIS Cloud Area Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLRLMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLRLMODIS",
        "units": "%",
        "description": "MODIS Cloud Area Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLTMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLTMODIS",
        "units": "%",
        "description": "MODIS Total Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CLWMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLWMODIS",
        "units": "%",
        "description": "MODIS Liquid Cloud Fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CO2_FFF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CO2_FFF",
        "units": "kg/kg",
        "description": "CO2_FFF",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CO2_LND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CO2_LND",
        "units": "kg/kg",
        "description": "CO2_LND",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CO2_OCN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CO2_OCN",
        "units": "kg/kg",
        "description": "CO2_OCN",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_a1DDF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a1DDF",
        "units": "kg/m2/s",
        "description": "dst_a1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_a1SFWET": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a1SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_a3DDF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a3DDF",
        "units": "kg/m2/s",
        "description": "dst_a3 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_a3SFWET": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a3SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_c1DDF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c1DDF",
        "units": "kg/m2/s",
        "description": "dst_c1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_c1SFWET": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c1SFWET",
        "units": "kg/m2/s",
        "description": "dst_c1 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_c1": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c1",
        "units": "kg/kg",
        "description": "dst_c1 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_c3DDF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c3DDF",
        "units": "kg/m2/s",
        "description": "dst_c3 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_c3SFWET": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c3SFWET",
        "units": "kg/m2/s",
        "description": "dst_c3 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dst_c3": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c3",
        "units": "kg/kg",
        "description": "dst_c3 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FISCCP1_COSP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FISCCP1_COSP",
        "units": "percent",
        "description": "Grid-box fraction covered by each ISCCP D level cloud type",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FREQI": {
        "standard_name": "specific_humidity",
        "cesm_name": "FREQI",
        "units": "fraction",
        "description": "Fractional occurrence of ice",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FREQL": {
        "standard_name": "specific_humidity",
        "cesm_name": "FREQL",
        "units": "fraction",
        "description": "Fractional occurrence of liquid",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ICIMR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ICIMR",
        "units": "kg/kg",
        "description": "Prognostic in-cloud ice mixing ratio",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ICWMR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ICWMR",
        "units": "kg/kg",
        "description": "Prognostic in-cloud water mixing ratio",
        "domain": "atmosphere",
        "component": "moar"
    },
    "IWC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "IWC",
        "units": "kg/m3",
        "description": "Grid box average ice water content",
        "domain": "atmosphere",
        "component": "moar"
    },
    "IWPMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "IWPMODIS",
        "units": "kg m-2",
        "description": "MODIS Cloud Ice Water Path time CLIMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LWPMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LWPMODIS",
        "units": "kg m-2",
        "description": "MODIS Cloud Liquid Water Path times CLWMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "MEANCLDALB_ISCCP": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "MEANCLDALB_ISCCP",
        "units": "1",
        "description": "Mean cloud albedo times CLDTOT_ISCCP",
        "domain": "atmosphere",
        "component": "moar"
    },
    "MEANPTOP_ISCCP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MEANPTOP_ISCCP",
        "units": "Pa",
        "description": "Mean cloud top pressure times CLDTOT_ISCCP",
        "domain": "atmosphere",
        "component": "moar"
    },
    "MEANTAU_ISCCP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MEANTAU_ISCCP",
        "units": "1",
        "description": "Mean optical thickness times CLDTOT_ISCCP",
        "domain": "atmosphere",
        "component": "moar"
    },
    "MEANTBCLR_ISCCP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MEANTBCLR_ISCCP",
        "units": "K",
        "description": "Mean Clear-sky Infrared Tb from ISCCP simulator",
        "domain": "atmosphere",
        "component": "moar"
    },
    "MEANTB_ISCCP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MEANTB_ISCCP",
        "units": "K",
        "description": "Mean Infrared Tb from ISCCP simulator",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_a1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a1DDF",
        "units": "kg/m2/s",
        "description": "ncl_a1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_a1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a1SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_a2DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a2DDF",
        "units": "kg/m2/s",
        "description": "ncl_a2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_a2SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a2SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_a3DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a3DDF",
        "units": "kg/m2/s",
        "description": "ncl_a3 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_a3SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a3SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c1DDF",
        "units": "kg/m2/s",
        "description": "ncl_c1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c1SFWET",
        "units": "kg/m2/s",
        "description": "ncl_c1 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c1",
        "units": "kg/kg",
        "description": "ncl_c1 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c2DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c2DDF",
        "units": "kg/m2/s",
        "description": "ncl_c2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c2SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c2SFWET",
        "units": "kg/m2/s",
        "description": "ncl_c2 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c2",
        "units": "kg/kg",
        "description": "ncl_c2 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c3DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c3DDF",
        "units": "kg/m2/s",
        "description": "ncl_c3 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c3SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c3SFWET",
        "units": "kg/m2/s",
        "description": "ncl_c3 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ncl_c3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_c3",
        "units": "kg/kg",
        "description": "ncl_c3 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_a1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a1DDF",
        "units": "1/m2/s",
        "description": "num_a1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_a1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a1SFWET",
        "units": "1/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_a2DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a2DDF",
        "units": "1/m2/s",
        "description": "num_a2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_a2SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a2SFWET",
        "units": "1/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_a3DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a3DDF",
        "units": "1/m2/s",
        "description": "num_a3 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_a3SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a3SFWET",
        "units": "1/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c1DDF",
        "units": "1/m2/s",
        "description": "num_c1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c1SFWET",
        "units": "1/m2/s",
        "description": "num_c1 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c1",
        "units": "1/kg",
        "description": "num_c1 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c2DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c2DDF",
        "units": "1/m2/s",
        "description": "num_c2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c2SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c2SFWET",
        "units": "1/m2/s",
        "description": "num_c2 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c2",
        "units": "1/kg",
        "description": "num_c2 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c3DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c3DDF",
        "units": "1/m2/s",
        "description": "num_c3 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c3SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c3SFWET",
        "units": "1/m2/s",
        "description": "num_c3 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "num_c3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c3",
        "units": "1/kg",
        "description": "num_c3 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "NUMLIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "NUMLIQ",
        "units": "1/kg",
        "description": "Grid box averaged cloud liquid number",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PCTMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PCTMODIS",
        "units": "Pa",
        "description": "MODIS Cloud Top Pressure times CLTMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "pom_a1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a1DDF",
        "units": "kg/m2/s",
        "description": "pom_a1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "pom_a1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a1SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "pom_c1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_c1DDF",
        "units": "kg/m2/s",
        "description": "pom_c1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "pom_c1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_c1SFWET",
        "units": "kg/m2/s",
        "description": "pom_c1 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "pom_c1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_c1",
        "units": "kg/kg",
        "description": "pom_c1 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "REFFCLIMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "REFFCLIMODIS",
        "units": "m",
        "description": "MODIS Ice Cloud Particle Size times CLIMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "REFFCLWMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "REFFCLWMODIS",
        "units": "m",
        "description": "MODIS Liquid Cloud Particle Size times CLWMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "RFL_PARASOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RFL_PARASOL",
        "units": "fraction",
        "description": "PARASOL-like mono-directional reflectance",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SFCO2_FFF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFCO2_FFF",
        "units": "kg/m2/s",
        "description": "CO2_FFF surface flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SFCO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFCO2",
        "units": "kg/m2/s",
        "description": "CO2 surface flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_a1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a1DDF",
        "units": "kg/m2/s",
        "description": "so4_a1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_a1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a1SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_a2DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2DDF",
        "units": "kg/m2/s",
        "description": "so4_a2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_a2SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_a3DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a3DDF",
        "units": "kg/m2/s",
        "description": "so4_a3 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_a3SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a3SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c1DDF",
        "units": "kg/m2/s",
        "description": "so4_c1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c1SFWET",
        "units": "kg/m2/s",
        "description": "so4_c1 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c1",
        "units": "kg/kg",
        "description": "so4_c1 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c2DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c2DDF",
        "units": "kg/m2/s",
        "description": "so4_c2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c2SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c2SFWET",
        "units": "kg/m2/s",
        "description": "so4_c2 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c2",
        "units": "kg/kg",
        "description": "so4_c2 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c3DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c3DDF",
        "units": "kg/m2/s",
        "description": "so4_c3 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c3SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c3SFWET",
        "units": "kg/m2/s",
        "description": "so4_c3 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "so4_c3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_c3",
        "units": "kg/kg",
        "description": "so4_c3 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "soa_a1DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_a1DDF",
        "units": "kg/m2/s",
        "description": "soa_a1 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "soa_a1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_a1SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "soa_a2DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_a2DDF",
        "units": "kg/m2/s",
        "description": "soa_a2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "soa_a2SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_a2SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "soa_c1SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_c1SFWET",
        "units": "kg/m2/s",
        "description": "soa_c1 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "soa_c1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_c1",
        "units": "kg/kg",
        "description": "soa_c1 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "soa_c2SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_c2SFWET",
        "units": "kg/m2/s",
        "description": "soa_c2 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "soa_c2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_c2",
        "units": "kg/kg",
        "description": "soa_c2 in cloud water",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TAUILOGMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUILOGMODIS",
        "units": "1",
        "description": "MODIS Ice Cloud Optical Thickness (Log10 Mean) times CLIMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TAUIMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUIMODIS",
        "units": "1",
        "description": "MODIS Ice Cloud Optical Thickness times CLIMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TAUTLOGMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUTLOGMODIS",
        "units": "1",
        "description": "MODIS Total Cloud Optical Thickness (Log10 Mean) times CLTMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TAUTMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUTMODIS",
        "units": "1",
        "description": "MODIS Total Cloud Optical Thickness times CLTMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TAUWLOGMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUWLOGMODIS",
        "units": "1",
        "description": "MODIS Liquid Cloud Optical Thickness (Log10 Mean) times CLWMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TAUWMODIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUWMODIS",
        "units": "1",
        "description": "MODIS Liquid Cloud Optical Thickness times CLWMODIS",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TMCO2_FFF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMCO2_FFF",
        "units": "kg/m2",
        "description": "CO2_FFF column burden",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TMCO2_LND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMCO2_LND",
        "units": "kg/m2",
        "description": "CO2_LND column burden",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TMCO2_OCN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMCO2_OCN",
        "units": "kg/m2",
        "description": "CO2_OCN column burden",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VD01": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VD01",
        "units": "kg/kg/s",
        "description": "Vertical diffusion of Q",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WSUB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WSUB",
        "units": "m/s",
        "description": "Diagnostic sub-grid vertical velocity",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ACTNI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ACTNI",
        "units": "m-3",
        "description": "Average Cloud Top ice number",
        "domain": "atmosphere",
        "component": "std"
    },
    "ACTNL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ACTNL",
        "units": "m-3",
        "description": "Average Cloud Top droplet number",
        "domain": "atmosphere",
        "component": "std"
    },
    "ACTREI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ACTREI",
        "units": "Micron",
        "description": "Average Cloud Top ice effective radius",
        "domain": "atmosphere",
        "component": "std"
    },
    "ACTREL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ACTREL",
        "units": "Micron",
        "description": "Average Cloud Top droplet effective radius",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODVIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODVIS",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm day only",
        "domain": "atmosphere",
        "component": "std"
    },
    "BURDENBCdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BURDENBCdn",
        "units": "kg/m2",
        "description": "Black carbon aerosol burden day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "BURDENDUSTdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BURDENDUSTdn",
        "units": "kg/m2",
        "description": "Dust aerosol burden day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "BURDENPOMdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BURDENPOMdn",
        "units": "kg/m2",
        "description": "POM aerosol burden day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "BURDENSEASALTdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BURDENSEASALTdn",
        "units": "kg/m2",
        "description": "Seasalt aerosol burden day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "BURDENSO4dn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BURDENSO4dn",
        "units": "kg/m2",
        "description": "Sulfate aerosol burden day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "BURDENSO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BURDENSO4",
        "units": "kg/m2",
        "description": "Sulfate aerosol burden day only",
        "domain": "atmosphere",
        "component": "std"
    },
    "BURDENSOAdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BURDENSOAdn",
        "units": "kg/m2",
        "description": "SOA aerosol burden day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "CDNUMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CDNUMC",
        "units": "1/m2",
        "description": "Vertically-integrated droplet concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "FCTI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FCTI",
        "units": "fraction",
        "description": "Fractional occurrence of cloud top ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "FCTL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FCTL",
        "units": "fraction",
        "description": "Fractional occurrence of cloud top liquid",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLDSC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLDSC",
        "units": "W/m2",
        "description": "Clearsky Downwelling longwave flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLDS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLDS",
        "units": "W/m^2",
        "description": "atmospheric longwave radiation (downscaled to columns in glacier regions)",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLNR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLNR",
        "units": "W/m2",
        "description": "Net longwave flux at tropopause",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLNSC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLNSC",
        "units": "W/m2",
        "description": "Clearsky net longwave flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLNS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLNS",
        "units": "W/m2",
        "description": "Net longwave flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLNTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLNTC",
        "units": "W/m2",
        "description": "Clearsky net longwave flux at top of model",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLNT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLNT",
        "units": "W/m2",
        "description": "Net longwave flux at top of model",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLUTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLUTC",
        "units": "W/m2",
        "description": "Clearsky upwelling longwave flux at top of model",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSDSC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDSC",
        "units": "W/m2",
        "description": "Clearsky downwelling solar flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSDS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDS",
        "units": "W/m^2",
        "description": "atmospheric incident solar radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNR",
        "units": "W/m2",
        "description": "Net solar flux at tropopause",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNSC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNSC",
        "units": "W/m2",
        "description": "Clearsky net solar flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNS",
        "units": "W/m2",
        "description": "Net solar flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNTOAC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNTOAC",
        "units": "W/m2",
        "description": "Clearsky net solar flux at top of atmosphere",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNT",
        "units": "W/m2",
        "description": "Net solar flux at top of model",
        "domain": "atmosphere",
        "component": "std"
    },
    "LWCF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LWCF",
        "units": "W/m2",
        "description": "Longwave cloud forcing",
        "domain": "atmosphere",
        "component": "std"
    },
    "MSKtem": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MSKtem",
        "units": "1",
        "description": "TEM mask",
        "domain": "atmosphere",
        "component": "std"
    },
    "OMEGA500": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "OMEGA500",
        "units": "Pa/s",
        "description": "Vertical velocity at 500 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "PBLH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PBLH",
        "units": "m",
        "description": "PBL height",
        "domain": "atmosphere",
        "component": "std"
    },
    "PHIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PHIS",
        "units": "m2/s2",
        "description": "Surface geopotential",
        "domain": "atmosphere",
        "component": "std"
    },
    "PRECSC": {
        "standard_name": "precipitation_flux",
        "cesm_name": "PRECSC",
        "units": "m/s",
        "description": "Convective snow rate (water equivalent)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PRECSL": {
        "standard_name": "precipitation_flux",
        "cesm_name": "PRECSL",
        "units": "m/s",
        "description": "Large-scale (stable) snow rate (water equivalent)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PRECTMX": {
        "standard_name": "precipitation_flux",
        "cesm_name": "PRECTMX",
        "units": "m/s",
        "description": "Maximum (convective and large-scale) precipitation rate (liq+ice)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PSL": {
        "standard_name": "air_pressure_at_mean_sea_level",
        "cesm_name": "PSL",
        "units": "Pa",
        "description": "Sea level pressure",
        "domain": "atmosphere",
        "component": "std"
    },
    "Q200": {
        "standard_name": "specific_humidity",
        "cesm_name": "Q200",
        "units": "kg/kg",
        "description": "Specific humidity at 200 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Q500": {
        "standard_name": "specific_humidity",
        "cesm_name": "Q500",
        "units": "kg/kg",
        "description": "Specific humidity at 500 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Q700": {
        "standard_name": "specific_humidity",
        "cesm_name": "Q700",
        "units": "Pa/s",
        "description": "Vertical velocity at 700 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Q850": {
        "standard_name": "specific_humidity",
        "cesm_name": "Q850",
        "units": "kg/kg",
        "description": "Specific humidity at 800 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "RHREFHT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RHREFHT",
        "units": "fraction",
        "description": "Reference height relative humidity",
        "domain": "atmosphere",
        "component": "std"
    },
    "SHFLX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SHFLX",
        "units": "W/m2",
        "description": "Surface sensible heat flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOLIN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOLIN",
        "units": "W/m2",
        "description": "Solar insolation",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOLLD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOLLD",
        "units": "W/m2",
        "description": "Solar downward near infrared diffuse to surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOLSD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOLSD",
        "units": "W/m2",
        "description": "Solar downward visible diffuse to surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "SWCF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SWCF",
        "units": "W/m2",
        "description": "Shortwave cloud forcing",
        "domain": "atmosphere",
        "component": "std"
    },
    "T010": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "T010",
        "units": "K",
        "description": "Temperature at 10 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "T200": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "T200",
        "units": "K",
        "description": "Temperature at 200 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "T500": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "T500",
        "units": "K",
        "description": "Temperature at 500 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "T700": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "T700",
        "units": "K",
        "description": "Temperature at 700 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "T850": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "T850",
        "units": "K",
        "description": "Temperature at 850 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUBLJX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUBLJX",
        "units": "N/m2",
        "description": "Zonal integrated drag from Beljaars SGO",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUBLJY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUBLJY",
        "units": "N/m2",
        "description": "Meridional integrated drag from Beljaars SGO",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUGWX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUGWX",
        "units": "N/m2",
        "description": "Zonal gravity wave surface stress",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUGWY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUGWY",
        "units": "N/m2",
        "description": "Meridional gravity wave surface stress",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUX",
        "units": "dyne/centimeter^2",
        "description": "Windstress in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUY",
        "units": "dyne/centimeter^2",
        "description": "Windstress in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "TGCLDIWP": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "TGCLDIWP",
        "units": "kg/m2",
        "description": "Total grid-box cloud ice water path",
        "domain": "atmosphere",
        "component": "std"
    },
    "TGCLDLWP": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "TGCLDLWP",
        "units": "kg/m2",
        "description": "Total grid-box cloud liquid water path",
        "domain": "atmosphere",
        "component": "std"
    },
    "TREFHTMN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TREFHTMN",
        "units": "K",
        "description": "Minimum reference height temperature over output period",
        "domain": "atmosphere",
        "component": "std"
    },
    "TREFHTMX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TREFHTMX",
        "units": "K",
        "description": "Maximum reference height temperature over output period",
        "domain": "atmosphere",
        "component": "std"
    },
    "TREFHT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TREFHT",
        "units": "K",
        "description": "Reference height temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSMN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSMN",
        "units": "K",
        "description": "Minimum surface temperature over output period",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSMX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSMX",
        "units": "K",
        "description": "Maximum surface temperature over output period",
        "domain": "atmosphere",
        "component": "std"
    },
    "U010": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "U010",
        "units": "m/s",
        "description": "Zonal wind at 10 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "U10": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "U10",
        "units": "m/s",
        "description": "10-m wind",
        "domain": "atmosphere",
        "component": "std"
    },
    "U200": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "U200",
        "units": "m/s",
        "description": "Zonal wind at 200 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "U500": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "U500",
        "units": "m/s",
        "description": "Zonal wind at 500 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "U700": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "U700",
        "units": "m/s",
        "description": "Zonal wind at 700 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "U850": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "U850",
        "units": "m/s",
        "description": "Zonal wind at 850 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "UV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UV",
        "units": "UNKNOWN",
        "description": "Momentum Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "V010": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "V010",
        "units": "m/s",
        "description": "Meridional wind at 10 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "V200": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "V200",
        "units": "m/s",
        "description": "Meridional wind at 200 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "V500": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "V500",
        "units": "m/s",
        "description": "Meridional wind at 200 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "V700": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "V700",
        "units": "m/s",
        "description": "Meridional wind at 700 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "V850": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "V850",
        "units": "m/s",
        "description": "Meridional wind at 850 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "VQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "VQ",
        "units": "m/skg/kg",
        "description": "Meridional water transport",
        "domain": "atmosphere",
        "component": "std"
    },
    "VT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VT",
        "units": "K m/s",
        "description": "Meridional heat transport",
        "domain": "atmosphere",
        "component": "std"
    },
    "VZ": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VZ",
        "units": "m2/s",
        "description": "Meridional transport of geopotential energy",
        "domain": "atmosphere",
        "component": "std"
    },
    "WSPDSRFAV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WSPDSRFAV",
        "units": "m/s",
        "description": "Horizontal total wind speed average at the surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "WSPDSRFMX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WSPDSRFMX",
        "units": "m/s",
        "description": "Horizontal total wind speed maximum at the surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Z050": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Z050",
        "units": "m",
        "description": "Geopotential Z at 50 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Z200": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Z200",
        "units": "m",
        "description": "Geopotential Z at 200 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Z500": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Z500",
        "units": "m",
        "description": "Geopotential height at 500 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Z700": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Z700",
        "units": "m",
        "description": "Geopotential Z at 700 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Z850": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Z850",
        "units": "m",
        "description": "Geopotential Z at 850 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "Z300": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Z300",
        "units": "m",
        "description": "Geopotential height at 300 mbar pressure surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABSORB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABSORB",
        "units": "/m",
        "description": "Aerosol absorption day only",
        "domain": "atmosphere",
        "component": "std"
    },
    "ac_CO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ac_CO2",
        "units": "kg m-2 s-1",
        "description": "aircraft emission ac_CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADRAIN": {
        "standard_name": "precipitation_flux",
        "cesm_name": "ADRAIN",
        "units": "Micron",
        "description": "Average rain effective Diameter",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADSNOW": {
        "standard_name": "snowfall_flux",
        "cesm_name": "ADSNOW",
        "units": "Micron",
        "description": "Average snow effective Diameter",
        "domain": "atmosphere",
        "component": "std"
    },
    "AEROD_v": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AEROD_v",
        "units": "1",
        "description": "Total Aerosol Optical Depth in visible band",
        "domain": "atmosphere",
        "component": "std"
    },
    "ANRAIN": {
        "standard_name": "precipitation_flux",
        "cesm_name": "ANRAIN",
        "units": "m-3",
        "description": "Average rain number conc",
        "domain": "atmosphere",
        "component": "std"
    },
    "ANSNOW": {
        "standard_name": "snowfall_flux",
        "cesm_name": "ANSNOW",
        "units": "m-3",
        "description": "Average snow number conc",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODABSdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODABSdn",
        "units": "no units",
        "description": "Aerosol absorption optical depth 550 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODBCdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODBCdn",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm from BC day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODdnDUST1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODdnDUST1",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm day night mode 1 from dust",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODdnDUST2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODdnDUST2",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm day night mode 2 from dust",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODdnDUST3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODdnDUST3",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm day night mode 3 from dust",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODdnMODE1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODdnMODE1",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm day night mode 1",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODdnMODE2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODdnMODE2",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm day night mode 2",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODdnMODE3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODdnMODE3",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm day night mode 3",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODDUST1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODDUST1",
        "units": "no units",
        "description": "Aerosol optical depth day only 550 nm mode 1 from dust",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODDUST2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODDUST2",
        "units": "Aerosol optical depth 550 nm model 2 from dust",
        "description": "SL",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODDUST3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODDUST3",
        "units": "no units",
        "description": "Aerosol optical depth day only 550 nm mode 3 from dust",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODDUST": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODDUST",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm from dust day only",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODNIRstdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODNIRstdn",
        "units": "no units",
        "description": "Stratospheric aerosol optical depth 1020 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODPOMdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODPOMdn",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm from POM day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODSO4dn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODSO4dn",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm from SO4 day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODSOAdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODSOAdn",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm from SOA day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODSSdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODSSdn",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm from seasalt day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODUVdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODUVdn",
        "units": "no units",
        "description": "Aerosol optical depth 350 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODUVstdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODUVstdn",
        "units": "no units",
        "description": "Stratospheric aerosol optical depth 350 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODVISdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODVISdn",
        "units": "no units",
        "description": "Aerosol optical depth 550 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AODVISstdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AODVISstdn",
        "units": "no units",
        "description": "Stratospheric aerosol optical depth 550 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "AQRAIN": {
        "standard_name": "precipitation_flux",
        "cesm_name": "AQRAIN",
        "units": "kg/kg",
        "description": "Average rain mixing ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "AQSNOW": {
        "standard_name": "snowfall_flux",
        "cesm_name": "AQSNOW",
        "units": "kg/kg",
        "description": "Average snow mixing ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "AQ_SO2": {
        "standard_name": "specific_humidity",
        "cesm_name": "AQ_SO2",
        "units": "kg/m2/s",
        "description": "SO2 aqueous chemistry (for gas species)",
        "domain": "atmosphere",
        "component": "std"
    },
    "AREA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AREA",
        "units": "m2",
        "description": "area of grid box",
        "domain": "atmosphere",
        "component": "std"
    },
    "AREI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AREI",
        "units": "Micron",
        "description": "Average ice effective radius",
        "domain": "atmosphere",
        "component": "std"
    },
    "AREL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AREL",
        "units": "Micron",
        "description": "Average droplet effective radius",
        "domain": "atmosphere",
        "component": "std"
    },
    "AWNC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AWNC",
        "units": "m-3",
        "description": "Average cloud water number conc",
        "domain": "atmosphere",
        "component": "std"
    },
    "AWNI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AWNI",
        "units": "m-3",
        "description": "Average cloud ice number conc",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_a1_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a1_SRF",
        "units": "kg/kg",
        "description": "bc_a1 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a1",
        "units": "kg/kg",
        "description": "bc_a1 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_a4_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a4_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for bc_a4",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_a4_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a4_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for bc_a4",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_a4DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a4DDF",
        "units": "kg/m2/s",
        "description": "bc_a4 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_a4SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a4SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_a4_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a4_SRF",
        "units": "kg/kg",
        "description": "bc_a4 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_a4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_a4",
        "units": "kg/kg",
        "description": "bc_a4 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_c4DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_c4DDF",
        "units": "kg/m2/s",
        "description": "bc_c4 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_c4SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_c4SFWET",
        "units": "kg/m2/s",
        "description": "bc_c4 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "bc_c4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bc_c4",
        "units": "kg/kg",
        "description": "bc_c4 in cloud water",
        "domain": "atmosphere",
        "component": "std"
    },
    "BROX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BROX",
        "units": "mol/mol",
        "description": "brox (Br+BrO+BRCl+HOBr)",
        "domain": "atmosphere",
        "component": "std"
    },
    "BROY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BROY",
        "units": "mol/mol",
        "description": "total inorganic bromine (Br+BrO+HOBr+BrONO2+HBr+BrCl)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CAPE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CAPE",
        "units": "J/kg",
        "description": "Convectively available potential energy",
        "domain": "atmosphere",
        "component": "std"
    },
    "CCN3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CCN3",
        "units": "#/cm3",
        "description": "CCN concentration at S=0.1%",
        "domain": "atmosphere",
        "component": "std"
    },
    "CLDHGH": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDHGH",
        "units": "fraction",
        "description": "Vertically-integrated high cloud",
        "domain": "atmosphere",
        "component": "std"
    },
    "CLDMED": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLDMED",
        "units": "fraction",
        "description": "Vertically-integrated mid-level cloud",
        "domain": "atmosphere",
        "component": "std"
    },
    "CLOUDCOVER_CLUBB": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLOUDCOVER_CLUBB",
        "units": "fraction",
        "description": "Cloud Cover",
        "domain": "atmosphere",
        "component": "std"
    },
    "CLOUDFRAC_CLUBB": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CLOUDFRAC_CLUBB",
        "units": "fraction",
        "description": "Cloud Fraction",
        "domain": "atmosphere",
        "component": "std"
    },
    "CLOX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLOX",
        "units": "mol/mol",
        "description": "clox (Cl+CLO+HOCl+2Cl2+2Cl2O2+OClO",
        "domain": "atmosphere",
        "component": "std"
    },
    "CLOY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CLOY",
        "units": "mol/mol",
        "description": "total inorganic chlorine (Cl+ClO+2Cl2+2Cl2O2+OClO+HOCl+ClONO2+HCl+BrCl)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CME": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CME",
        "units": "kg/kg/s",
        "description": "Rate of cond-evap within the cloud",
        "domain": "atmosphere",
        "component": "std"
    },
    "CMFDQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "CMFDQ",
        "units": "kg/kg/s",
        "description": "QV tendency - shallow convection",
        "domain": "atmosphere",
        "component": "std"
    },
    "CO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CO2",
        "units": "kg/kg",
        "description": "CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "CONCLD": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "CONCLD",
        "units": "fraction",
        "description": "Convective cloud cover",
        "domain": "atmosphere",
        "component": "std"
    },
    "DF_H2O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DF_H2O2",
        "units": "kg/m2/s",
        "description": "dry deposition flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DF_H2SO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DF_H2SO4",
        "units": "kg/m2/s",
        "description": "dry deposition flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DF_SO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DF_SO2",
        "units": "kg/m2/s",
        "description": "dry deposition flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "dgnumwet1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dgnumwet1",
        "units": "m",
        "description": "Aerosol mode wet diameter",
        "domain": "atmosphere",
        "component": "std"
    },
    "dgnumwet2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dgnumwet2",
        "units": "m",
        "description": "Aerosol mode wet diameter",
        "domain": "atmosphere",
        "component": "std"
    },
    "dgnumwet3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dgnumwet3",
        "units": "m",
        "description": "Aerosol mode wet diameter",
        "domain": "atmosphere",
        "component": "std"
    },
    "DH2O2CHM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DH2O2CHM",
        "units": "kg/s",
        "description": "net tendency from chem",
        "domain": "atmosphere",
        "component": "std"
    },
    "DMS_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DMS_SRF",
        "units": "mol/mol",
        "description": "DMS in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "DMS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DMS",
        "units": "mol/mol",
        "description": "DMS concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "dry_deposition_NHx_as_N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dry_deposition_NHx_as_N",
        "units": "kg/m2/s",
        "description": "NHx dry deposition flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "dry_deposition_NOy_as_N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dry_deposition_NOy_as_N",
        "units": "kg/m2/s",
        "description": "NOy dry deposition flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "Dso4_a1CHM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Dso4_a1CHM",
        "units": "kg/s",
        "description": "net tendency from chem",
        "domain": "atmosphere",
        "component": "std"
    },
    "Dso4_a2CHM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Dso4_a2CHM",
        "units": "kg/s",
        "description": "net tendency from chem",
        "domain": "atmosphere",
        "component": "std"
    },
    "Dso4_a3CHM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Dso4_a3CHM",
        "units": "kg/s",
        "description": "net tendency from chem",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a1SF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a1SF",
        "units": "kg/m2/s",
        "description": "dst_a1 dust surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a1_SRF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a1_SRF",
        "units": "kg/kg",
        "description": "dst_a1 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a1": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a1",
        "units": "kg/kg",
        "description": "dst_a1 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a2DDF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a2DDF",
        "units": "kg/m2/s",
        "description": "dst_a2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a2SF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a2SF",
        "units": "kg/m2/s",
        "description": "dst_a2 dust surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a2SFWET": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a2SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a2_SRF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a2_SRF",
        "units": "kg/kg",
        "description": "dst_a2 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a2": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a2",
        "units": "kg/kg",
        "description": "dst_a2 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a3SF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a3SF",
        "units": "kg/m2/s",
        "description": "dst_a3 dust surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a3_SRF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a3_SRF",
        "units": "kg/kg",
        "description": "dst_a3 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_a3": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_a3",
        "units": "kg/kg",
        "description": "dst_a3 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_c2DDF": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c2DDF",
        "units": "kg/m2/s",
        "description": "dst_c2 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_c2SFWET": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c2SFWET",
        "units": "kg/m2/s",
        "description": "dst_c2 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "dst_c2": {
        "standard_name": "air_temperature",
        "cesm_name": "dst_c2",
        "units": "kg/kg",
        "description": "dst_c2 in cloud water",
        "domain": "atmosphere",
        "component": "std"
    },
    "DTCORE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DTCORE",
        "units": "K/s",
        "description": "T tendency due to dynamical core",
        "domain": "atmosphere",
        "component": "std"
    },
    "DTWR_H2O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DTWR_H2O2",
        "units": "kg/kg/s",
        "description": "wet removal Neu scheme tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "DTWR_H2SO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DTWR_H2SO4",
        "units": "kg/kg/s",
        "description": "wet removal Neu scheme tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "DTWR_SO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DTWR_SO2",
        "units": "kg/kg/s",
        "description": "wet removal Neu scheme tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "EVAPPREC": {
        "standard_name": "precipitation_flux",
        "cesm_name": "EVAPPREC",
        "units": "kg/kg/s",
        "description": "Rate of evaporation of falling precip",
        "domain": "atmosphere",
        "component": "std"
    },
    "EVAPQZM": {
        "standard_name": "specific_humidity",
        "cesm_name": "EVAPQZM",
        "units": "kg/kg/s",
        "description": "Q tendency - Evaporation from Zhang-McFarlane moist convection",
        "domain": "atmosphere",
        "component": "std"
    },
    "EVAPTZM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EVAPTZM",
        "units": "K/s",
        "description": "T tendency - Evaporation/snow prod from Zhang convection",
        "domain": "atmosphere",
        "component": "std"
    },
    "EXTINCTdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EXTINCTdn",
        "units": "/m",
        "description": "Aerosol extinction 550 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "EXTINCTNIRdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EXTINCTNIRdn",
        "units": "/m",
        "description": "Aerosol extinction 1020 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "EXTINCTUVdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EXTINCTUVdn",
        "units": "/m",
        "description": "Aerosol extinction 350 nm day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "EXTxASYMdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EXTxASYMdn",
        "units": "no units",
        "description": "extinction 550 times asymmetry factor day night",
        "domain": "atmosphere",
        "component": "std"
    },
    "FICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FICE",
        "units": "fraction",
        "description": "Fractional ice content within cloud",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLNTCLR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLNTCLR",
        "units": "W/m2",
        "description": "Clearsky ONLY points net longwave flux at top of model",
        "domain": "atmosphere",
        "component": "std"
    },
    "FREQCLR": {
        "standard_name": "specific_humidity",
        "cesm_name": "FREQCLR",
        "units": "Frac",
        "description": "Frequency of Occurrence of Clearsky",
        "domain": "atmosphere",
        "component": "std"
    },
    "FREQR": {
        "standard_name": "specific_humidity",
        "cesm_name": "FREQR",
        "units": "fraction",
        "description": "Fractional occurrence of rain",
        "domain": "atmosphere",
        "component": "std"
    },
    "FREQS": {
        "standard_name": "specific_humidity",
        "cesm_name": "FREQS",
        "units": "fraction",
        "description": "Fractional occurrence of snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "FREQZM": {
        "standard_name": "specific_humidity",
        "cesm_name": "FREQZM",
        "units": "fraction",
        "description": "Fractional occurance of ZM convection",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNTC",
        "units": "W/m2",
        "description": "Clearsky net solar flux at top of model",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSUTOA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSUTOA",
        "units": "W/m2",
        "description": "Upwelling solar flux at top of atmosphere",
        "domain": "atmosphere",
        "component": "std"
    },
    "GS_SO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GS_SO2",
        "units": "kg/m2/s",
        "description": "SO2 gas chemistry/wet removal (for gas species)",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2O2_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2O2_SRF",
        "units": "mol/mol",
        "description": "H2O2 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2O2",
        "units": "mol/mol",
        "description": "H2O2 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2O_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2O_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for H2O",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2O_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2O_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for H2O",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2O_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2O_SRF",
        "units": "mol/mol",
        "description": "water vapor in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2O": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2O",
        "units": "mol/mol",
        "description": "water vapor concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2SO4M_C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2SO4M_C",
        "units": "ug/m3",
        "description": "chemical sulfate aerosol mass",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2SO4_sfnnuc1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2SO4_sfnnuc1",
        "units": "kg/m2/s",
        "description": "H2SO4 modal_aero new particle nucleation column tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2SO4_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2SO4_SRF",
        "units": "mol/mol",
        "description": "H2SO4 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2SO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2SO4",
        "units": "mol/mol",
        "description": "H2SO4 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "HCL_GAS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HCL_GAS",
        "units": "mol/mol",
        "description": "gas-phase hcl",
        "domain": "atmosphere",
        "component": "std"
    },
    "HNO3_GAS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HNO3_GAS",
        "units": "mol/mol",
        "description": "gas-phase hno3",
        "domain": "atmosphere",
        "component": "std"
    },
    "HNO3_NAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HNO3_NAT",
        "units": "mol/mol",
        "description": "NAT condensed HNO3",
        "domain": "atmosphere",
        "component": "std"
    },
    "HNO3_STS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HNO3_STS",
        "units": "mol/mol",
        "description": "STS condensed HNO3",
        "domain": "atmosphere",
        "component": "std"
    },
    "HO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HO2",
        "units": "mol/mol",
        "description": "prescribed tracer constituent",
        "domain": "atmosphere",
        "component": "std"
    },
    "ICEFRAC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ICEFRAC",
        "units": "fraction",
        "description": "Fraction of sfc area covered by sea-ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "jh2o2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "jh2o2",
        "units": "/s",
        "description": "photolysis rate constant",
        "domain": "atmosphere",
        "component": "std"
    },
    "KVH_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "KVH_CLUBB",
        "units": "m2/s",
        "description": "CLUBB vertical diffusivity of heat/moisture on interface levels",
        "domain": "atmosphere",
        "component": "std"
    },
    "LANDFRAC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LANDFRAC",
        "units": "fraction",
        "description": "Fraction of sfc area covered by land",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a1SF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a1SF",
        "units": "kg/m2/s",
        "description": "ncl_a1 seasalt surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a1_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a1_SRF",
        "units": "kg/kg",
        "description": "ncl_a1 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a1",
        "units": "kg/kg",
        "description": "ncl_a1 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a2SF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a2SF",
        "units": "kg/m2/s",
        "description": "ncl_a2 seasalt surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a2_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a2_SRF",
        "units": "kg/kg",
        "description": "ncl_a2 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a2",
        "units": "kg/kg",
        "description": "ncl_a2 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a3SF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a3SF",
        "units": "kg/m2/s",
        "description": "ncl_a3 seasalt surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a3_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a3_SRF",
        "units": "kg/kg",
        "description": "ncl_a3 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "ncl_a3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ncl_a3",
        "units": "kg/kg",
        "description": "ncl_a3 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "NITROP_PD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NITROP_PD",
        "units": "no units",
        "description": "Chemical Tropopause probability",
        "domain": "atmosphere",
        "component": "std"
    },
    "NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NO3",
        "units": "mmol/m^3",
        "description": "Dissolved Inorganic Nitrate",
        "domain": "atmosphere",
        "component": "std"
    },
    "NOX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NOX",
        "units": "mol/mol",
        "description": "nox (N+NO+NO2)",
        "domain": "atmosphere",
        "component": "std"
    },
    "NOY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NOY",
        "units": "mol/mol",
        "description": "noy = total nitrogen (N+NO+NO2+NO3+2N2O5+HNO3+HO2NO2+ORGNOY+NH4NO3",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a1_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a1_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for num_a1",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a1_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a1_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for num_a1",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a1SF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a1SF",
        "units": "kg/m2/s",
        "description": "num_a1 dust surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a1_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a1_SRF",
        "units": "1/kg",
        "description": "num_a1 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a1",
        "units": "1/kg",
        "description": "num_a1 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a2_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a2_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for num_a2",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a2_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a2_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for num_a2",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a2_sfnnuc1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a2_sfnnuc1",
        "units": "#/m2/s",
        "description": "num_a2 modal_aero new particle nucleation column tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a2SF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a2SF",
        "units": "kg/m2/s",
        "description": "num_a2 dust surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a2_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a2_SRF",
        "units": "1/kg",
        "description": "num_a2 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a2",
        "units": "1/kg",
        "description": "num_a2 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a3SF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a3SF",
        "units": "kg/m2/s",
        "description": "num_a3 dust surface emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a3_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a3_SRF",
        "units": "1/kg",
        "description": "num_a3 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a3",
        "units": "1/kg",
        "description": "num_a3 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a4_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a4_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for num_a4",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a4_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a4_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for num_a4",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a4DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a4DDF",
        "units": "1/m2/s",
        "description": "num_a4 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a4SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a4SFWET",
        "units": "1/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a4_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a4_SRF",
        "units": "1/kg",
        "description": "num_a4 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_a4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_a4",
        "units": "1/kg",
        "description": "num_a4 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_c4DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c4DDF",
        "units": "1/m2/s",
        "description": "num_c4 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_c4SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c4SFWET",
        "units": "1/m2/s",
        "description": "num_c4 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "num_c4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "num_c4",
        "units": "1/kg",
        "description": "num_c4 in cloud water",
        "domain": "atmosphere",
        "component": "std"
    },
    "NUMICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NUMICE",
        "units": "1/kg",
        "description": "Grid box averaged cloud ice number",
        "domain": "atmosphere",
        "component": "std"
    },
    "NUMRAI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NUMRAI",
        "units": "1/kg",
        "description": "Grid box averaged rain number",
        "domain": "atmosphere",
        "component": "std"
    },
    "NUMSNO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NUMSNO",
        "units": "1/kg",
        "description": "Grid box averaged snow number",
        "domain": "atmosphere",
        "component": "std"
    },
    "O3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "O3",
        "units": "mol/mol",
        "description": "prescribed tracer constituent",
        "domain": "atmosphere",
        "component": "std"
    },
    "OCNFRAC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "OCNFRAC",
        "units": "fraction",
        "description": "Fraction of sfc area covered by ocean",
        "domain": "atmosphere",
        "component": "std"
    },
    "OH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "OH",
        "units": "mol/mol",
        "description": "prescribed tracer constituent",
        "domain": "atmosphere",
        "component": "std"
    },
    "OMEGAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "OMEGAT",
        "units": "K Pa/s",
        "description": "Vertical heat flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_a1_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a1_SRF",
        "units": "kg/kg",
        "description": "pom_a1 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a1",
        "units": "kg/kg",
        "description": "pom_a1 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_a4_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a4_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for pom_a4",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_a4_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a4_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for pom_a4",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_a4DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a4DDF",
        "units": "kg/m2/s",
        "description": "pom_a4 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_a4SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a4SFWET",
        "units": "kg/m2/s",
        "description": "Wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_a4_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a4_SRF",
        "units": "kg/kg",
        "description": "pom_a4 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_a4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_a4",
        "units": "kg/kg",
        "description": "pom_a4 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_c4DDF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_c4DDF",
        "units": "kg/m2/s",
        "description": "pom_c4 dry deposition flux at bottom (grav+turb)",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_c4SFWET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_c4SFWET",
        "units": "kg/m2/s",
        "description": "pom_c4 wet deposition flux at surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "pom_c4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pom_c4",
        "units": "kg/kg",
        "description": "pom_c4 in cloud water",
        "domain": "atmosphere",
        "component": "std"
    },
    "PTEQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "PTEQ",
        "units": "kg/kg/s",
        "description": "Q total physics tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "PTTEND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PTTEND",
        "units": "K/s",
        "description": "T total physics tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLX": {
        "standard_name": "specific_humidity",
        "cesm_name": "QFLX",
        "units": "kg/m2/s",
        "description": "Surface water flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRAIN": {
        "standard_name": "precipitation_flux",
        "cesm_name": "QRAIN",
        "units": "kg/kg",
        "description": "Diagnostic grid-mean rain mixing ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRLC": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRLC",
        "units": "K/s",
        "description": "Clearsky longwave heating rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRSC": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRSC",
        "units": "K/s",
        "description": "Clearsky solar heating rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "QT": {
        "standard_name": "specific_humidity",
        "cesm_name": "QT",
        "units": "kg/kg",
        "description": "Total water mixing ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "RAD_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RAD_ICE",
        "units": "cm",
        "description": "sad ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "RAD_LNAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RAD_LNAT",
        "units": "cm",
        "description": "large nat radius",
        "domain": "atmosphere",
        "component": "std"
    },
    "RAD_SULFC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RAD_SULFC",
        "units": "cm",
        "description": "chemical sad sulfate",
        "domain": "atmosphere",
        "component": "std"
    },
    "RAINQM": {
        "standard_name": "precipitation_flux",
        "cesm_name": "RAINQM",
        "units": "kg/kg",
        "description": "Grid box averaged rain amount",
        "domain": "atmosphere",
        "component": "std"
    },
    "RCM_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RCM_CLUBB",
        "units": "g/kg",
        "description": "Cloud Water Mixing Ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "RCMINLAYER_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RCMINLAYER_CLUBB",
        "units": "g/kg",
        "description": "Cloud Water in Layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "RCMTEND_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RCMTEND_CLUBB",
        "units": "g/kg /s",
        "description": "Cloud Liquid Water Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "REFF_AERO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "REFF_AERO",
        "units": "cm",
        "description": "aerosol effective radius",
        "domain": "atmosphere",
        "component": "std"
    },
    "RELVAR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RELVAR",
        "units": "no units",
        "description": "Relative cloud water variance",
        "domain": "atmosphere",
        "component": "std"
    },
    "RHO_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RHO_CLUBB",
        "units": "kg/m3",
        "description": "Air Density",
        "domain": "atmosphere",
        "component": "std"
    },
    "RIMTEND_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RIMTEND_CLUBB",
        "units": "g/kg /s",
        "description": "Cloud Ice Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "RTP2_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RTP2_CLUBB",
        "units": "g^2/kg^2",
        "description": "Moisture Variance",
        "domain": "atmosphere",
        "component": "std"
    },
    "RTPTHLP_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RTPTHLP_CLUBB",
        "units": "K g/kg",
        "description": "Temp. Moist. Covariance",
        "domain": "atmosphere",
        "component": "std"
    },
    "RVMTEND_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RVMTEND_CLUBB",
        "units": "g/kg /s",
        "description": "Water vapor tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "SAD_AERO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SAD_AERO",
        "units": "cm2/cm3",
        "description": "aerosol surface area density",
        "domain": "atmosphere",
        "component": "std"
    },
    "SAD_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SAD_ICE",
        "units": "cm2/cm3",
        "description": "water-ice aerosol SAD",
        "domain": "atmosphere",
        "component": "std"
    },
    "SAD_LNAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SAD_LNAT",
        "units": "cm2/cm3",
        "description": "large-mode NAT aerosol SAD",
        "domain": "atmosphere",
        "component": "std"
    },
    "SAD_SULFC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SAD_SULFC",
        "units": "cm2/cm3",
        "description": "chemical sulfate aerosol SAD",
        "domain": "atmosphere",
        "component": "std"
    },
    "SAD_TROP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SAD_TROP",
        "units": "cm2/cm3",
        "description": "tropospheric aerosol SAD",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFbc_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFbc_a1",
        "units": "kg/m2/s",
        "description": "bc_a1 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFbc_a4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFbc_a4",
        "units": "kg/m2/s",
        "description": "bc_a4 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFCO2_LND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFCO2_LND",
        "units": "kg/m2/s",
        "description": "CO2_LND surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFCO2_OCN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFCO2_OCN",
        "units": "kg/m2/s",
        "description": "CO2_OCN surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFDMS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFDMS",
        "units": "kg/m2/s",
        "description": "DMS surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFdst_a1": {
        "standard_name": "air_temperature",
        "cesm_name": "SFdst_a1",
        "units": "kg/m2/s",
        "description": "dst_a1 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFdst_a2": {
        "standard_name": "air_temperature",
        "cesm_name": "SFdst_a2",
        "units": "kg/m2/s",
        "description": "dst_a2 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFdst_a3": {
        "standard_name": "air_temperature",
        "cesm_name": "SFdst_a3",
        "units": "kg/m2/s",
        "description": "dst_a3 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFH2O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFH2O2",
        "units": "kg/m2/s",
        "description": "H2O2 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFH2SO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFH2SO4",
        "units": "kg/m2/s",
        "description": "H2SO4 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFncl_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFncl_a1",
        "units": "kg/m2/s",
        "description": "ncl_a1 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFncl_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFncl_a2",
        "units": "kg/m2/s",
        "description": "ncl_a2 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFncl_a3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFncl_a3",
        "units": "kg/m2/s",
        "description": "ncl_a3 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFnum_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFnum_a1",
        "units": "1/m2/s",
        "description": "num_a1 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFnum_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFnum_a2",
        "units": "1/m2/s",
        "description": "num_a2 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFnum_a3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFnum_a3",
        "units": "1/m2/s",
        "description": "num_a3 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFnum_a4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFnum_a4",
        "units": "1/m2/s",
        "description": "num_a4 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFpom_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFpom_a1",
        "units": "kg/m2/s",
        "description": "pom_a1 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFpom_a4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFpom_a4",
        "units": "kg/m2/s",
        "description": "pom_a4 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFSO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFSO2",
        "units": "kg/m2/s",
        "description": "SO2 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFso4_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFso4_a1",
        "units": "kg/m2/s",
        "description": "so4_a1 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFso4_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFso4_a2",
        "units": "kg/m2/s",
        "description": "so4_a2 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFso4_a3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFso4_a3",
        "units": "kg/m2/s",
        "description": "so4_a3 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFsoa_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFsoa_a1",
        "units": "kg/m2/s",
        "description": "soa_a1 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFsoa_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFsoa_a2",
        "units": "kg/m2/s",
        "description": "soa_a2 surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFSOAG": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFSOAG",
        "units": "kg/m2/s",
        "description": "SOAG surface flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SL",
        "units": "J/kg",
        "description": "Liquid water static energy",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOWHICE": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOWHICE",
        "units": "m",
        "description": "Snow depth over ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOWHLND": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOWHLND",
        "units": "m",
        "description": "Water equivalent snow depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOWQM": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOWQM",
        "units": "kg/kg",
        "description": "Grid box averaged snow amount",
        "domain": "atmosphere",
        "component": "std"
    },
    "SO2_CHML": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SO2_CHML",
        "units": "/cm3/s",
        "description": "chemical loss rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "SO2_CHMP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SO2_CHMP",
        "units": "/cm3/s",
        "description": "chemical production rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "SO2_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SO2_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for SO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "SO2_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SO2_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for SO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "SO2_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SO2_SRF",
        "units": "mol/mol",
        "description": "SO2 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "SO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SO2",
        "units": "mol/mol",
        "description": "SO2 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "SO2_XFRC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SO2_XFRC",
        "units": "molec/cm3/s",
        "description": "external forcing for SO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a1_CHMP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a1_CHMP",
        "units": "/cm3/s",
        "description": "chemical production rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a1_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a1_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for so4_a1",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a1_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a1_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for so4_a1",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a1_sfgaex1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a1_sfgaex1",
        "units": "kg/m2/s",
        "description": "so4_a1 gas-aerosol-exchange primary column tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a1_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a1_SRF",
        "units": "kg/kg",
        "description": "so4_a1 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a1",
        "units": "kg/kg",
        "description": "so4_a1 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a2_CHMP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2_CHMP",
        "units": "/cm3/s",
        "description": "chemical production rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a2_CLXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2_CLXF",
        "units": "molec/cm2/s",
        "description": "vertically intergrated external forcing for so4_a2",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a2_CMXF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2_CMXF",
        "units": "kg/m2/s",
        "description": "vertically intergrated external forcing for so4_a2",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a2_sfgaex1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2_sfgaex1",
        "units": "kg/m2/s",
        "description": "so4_a2 gas-aerosol-exchange primary column tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a2_sfnnuc1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2_sfnnuc1",
        "units": "kg/m2/s",
        "description": "so4_a2 modal_aero new particle nucleation column tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a2_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2_SRF",
        "units": "kg/kg",
        "description": "so4_a2 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a2",
        "units": "kg/kg",
        "description": "so4_a2 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a3_sfgaex1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a3_sfgaex1",
        "units": "kg/m2/s",
        "description": "so4_a3 gas-aerosol-exchange primary column tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a3_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a3_SRF",
        "units": "kg/kg",
        "description": "so4_a3 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_a3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "so4_a3",
        "units": "kg/kg",
        "description": "so4_a3 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_c1AQH2SO4": {
        "standard_name": "specific_humidity",
        "cesm_name": "so4_c1AQH2SO4",
        "units": "kg/m2/s",
        "description": "so4_c1 aqueous phase chemistry",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_c1AQSO4": {
        "standard_name": "specific_humidity",
        "cesm_name": "so4_c1AQSO4",
        "units": "kg/m2/s",
        "description": "so4_c1 aqueous phase chemistry",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_c2AQH2SO4": {
        "standard_name": "specific_humidity",
        "cesm_name": "so4_c2AQH2SO4",
        "units": "kg/m2/s",
        "description": "so4_c2 aqueous phase chemistry",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_c2AQSO4": {
        "standard_name": "specific_humidity",
        "cesm_name": "so4_c2AQSO4",
        "units": "kg/m2/s",
        "description": "so4_c2 aqueous phase chemistry",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_c3AQH2SO4": {
        "standard_name": "specific_humidity",
        "cesm_name": "so4_c3AQH2SO4",
        "units": "kg/m2/s",
        "description": "so4_c3 aqueous phase chemistry",
        "domain": "atmosphere",
        "component": "std"
    },
    "so4_c3AQSO4": {
        "standard_name": "specific_humidity",
        "cesm_name": "so4_c3AQSO4",
        "units": "kg/m2/s",
        "description": "so4_c3 aqueous phase chemistry",
        "domain": "atmosphere",
        "component": "std"
    },
    "soa_a1_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_a1_SRF",
        "units": "kg/kg",
        "description": "soa_a1 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "soa_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_a1",
        "units": "kg/kg",
        "description": "soa_a1 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "soa_a2_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_a2_SRF",
        "units": "kg/kg",
        "description": "soa_a2 in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "soa_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "soa_a2",
        "units": "kg/kg",
        "description": "soa_a2 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOAG_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOAG_SRF",
        "units": "mol/mol",
        "description": "SOAG in bottom layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOAG": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOAG",
        "units": "mol/mol",
        "description": "SOAG concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "SSAVIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SSAVIS",
        "units": "no units",
        "description": "Aerosol single-scatter albedo day only",
        "domain": "atmosphere",
        "component": "std"
    },
    "SST": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SST",
        "units": "degC",
        "description": "Surface Potential Temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "STEND_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STEND_CLUBB",
        "units": "k/s",
        "description": "Temperature tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "TAQ",
        "units": "kg/kg/s",
        "description": "Q horz+vert+fixer tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "TBRY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TBRY",
        "units": "mol/mol",
        "description": "total Br (ORG+INORG) volume mixing ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "TCLY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TCLY",
        "units": "mol/mol",
        "description": "total Cl (ORG+INORG) volume mixing ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "TGCLDCWP": {
        "standard_name": "cloud_area_fraction",
        "cesm_name": "TGCLDCWP",
        "units": "kg/m2",
        "description": "Total grid-box cloud water path (liquid and ice)",
        "domain": "atmosphere",
        "component": "std"
    },
    "THLP2_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "THLP2_CLUBB",
        "units": "K^2",
        "description": "Temperature Variance",
        "domain": "atmosphere",
        "component": "std"
    },
    "TH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TH",
        "units": "K",
        "description": "Potential Temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TMCO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMCO2",
        "units": "kg/m2",
        "description": "CO2 column burden",
        "domain": "atmosphere",
        "component": "std"
    },
    "TMDMS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMDMS",
        "units": "kg/m2",
        "description": "DMS column burden",
        "domain": "atmosphere",
        "component": "std"
    },
    "TMSO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMSO2",
        "units": "kg/m2",
        "description": "SO2 column burden",
        "domain": "atmosphere",
        "component": "std"
    },
    "TMso4_a1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMso4_a1",
        "units": "kg/m2",
        "description": "so4_a1 column burden",
        "domain": "atmosphere",
        "component": "std"
    },
    "TMso4_a2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMso4_a2",
        "units": "kg/m2",
        "description": "so4_a2 column burden",
        "domain": "atmosphere",
        "component": "std"
    },
    "TMso4_a3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMso4_a3",
        "units": "kg/m2",
        "description": "so4_a3 column burden",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOT_CLD_VISTAU": {
        "standard_name": "air_temperature",
        "cesm_name": "TOT_CLD_VISTAU",
        "units": "1",
        "description": "Total gbx cloud extinction visible sw optical depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTH",
        "units": "mol/mol",
        "description": "total H2 volume mixing ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "TROP_P": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TROP_P",
        "units": "Pa",
        "description": "Tropopause Pressure",
        "domain": "atmosphere",
        "component": "std"
    },
    "TROP_T": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TROP_T",
        "units": "K",
        "description": "Tropopause Temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TROP_Z": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TROP_Z",
        "units": "m",
        "description": "Tropopause Height",
        "domain": "atmosphere",
        "component": "std"
    },
    "TTEND_TOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TTEND_TOT",
        "units": "K/s",
        "description": "Total temperature tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "TTGWORO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TTGWORO",
        "units": "K/s",
        "description": "T tendency - orographic gravity wave drag",
        "domain": "atmosphere",
        "component": "std"
    },
    "UM_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UM_CLUBB",
        "units": "m/s",
        "description": "Zonal Wind",
        "domain": "atmosphere",
        "component": "std"
    },
    "UP2_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UP2_CLUBB",
        "units": "m2/s2",
        "description": "Zonal Velocity Variance",
        "domain": "atmosphere",
        "component": "std"
    },
    "UPWP_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UPWP_CLUBB",
        "units": "m2/s2",
        "description": "Zonal Momentum Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "UTEND_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UTEND_CLUBB",
        "units": "m/s /s",
        "description": "U-wind Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "UU": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UU",
        "units": "m2/s2",
        "description": "Zonal velocity squared",
        "domain": "atmosphere",
        "component": "std"
    },
    "VM_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VM_CLUBB",
        "units": "m/s",
        "description": "Meridional Wind",
        "domain": "atmosphere",
        "component": "std"
    },
    "VP2_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VP2_CLUBB",
        "units": "m2/s2",
        "description": "Meridional Velocity Variance",
        "domain": "atmosphere",
        "component": "std"
    },
    "VPWP_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VPWP_CLUBB",
        "units": "m2/s2",
        "description": "Meridional Momentum Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "VTEND_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VTEND_CLUBB",
        "units": "m/s /s",
        "description": "V-wind Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "VU": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VU",
        "units": "m2/s2",
        "description": "Meridional flux of zonal momentum",
        "domain": "atmosphere",
        "component": "std"
    },
    "VV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VV",
        "units": "m2/s2",
        "description": "Meridional velocity squared",
        "domain": "atmosphere",
        "component": "std"
    },
    "WD_H2O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WD_H2O2",
        "units": "kg/m2/s",
        "description": "vertical integrated wet deposition flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "WD_H2SO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WD_H2SO4",
        "units": "kg/m2/s",
        "description": "vertical integrated wet deposition flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "WD_SO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WD_SO2",
        "units": "kg/m2/s",
        "description": "vertical integrated wet deposition flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "wet_deposition_NHx_as_N": {
        "standard_name": "air_temperature",
        "cesm_name": "wet_deposition_NHx_as_N",
        "units": "kg/m2/s",
        "description": "NHx wet deposition",
        "domain": "atmosphere",
        "component": "std"
    },
    "wet_deposition_NOy_as_N": {
        "standard_name": "air_temperature",
        "cesm_name": "wet_deposition_NOy_as_N",
        "units": "kg/m2/s",
        "description": "NOy wet deposition",
        "domain": "atmosphere",
        "component": "std"
    },
    "WP2_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WP2_CLUBB",
        "units": "m2/s2",
        "description": "Vertical Velocity Variance",
        "domain": "atmosphere",
        "component": "std"
    },
    "WP3_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WP3_CLUBB",
        "units": "m3/s3",
        "description": "Third Moment Vertical Velocity",
        "domain": "atmosphere",
        "component": "std"
    },
    "WPRCP_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WPRCP_CLUBB",
        "units": "W/m2",
        "description": "Liquid Water Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "WPRTP_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WPRTP_CLUBB",
        "units": "W/m2",
        "description": "Moisture Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "WPTHLP_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WPTHLP_CLUBB",
        "units": "W/m2",
        "description": "Heat Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "WPTHVP_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WPTHVP_CLUBB",
        "units": "W/m2",
        "description": "Buoyancy Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "WTHzm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WTHzm",
        "units": "MK/S",
        "description": "Vertical Heat Flux: 3D zon. mean",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZM_CLUBB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ZM_CLUBB",
        "units": "m",
        "description": "Momentum Heights",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZMDQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "ZMDQ",
        "units": "kg/kg/s",
        "description": "Q tendency - Zhang-McFarlane moist convection",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZMDT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ZMDT",
        "units": "K/s",
        "description": "T tendency - Zhang-McFarlane moist convection",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZMMTT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ZMMTT",
        "units": "K/s",
        "description": "T tendency - ZM convective momentum transport",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZMMU": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ZMMU",
        "units": "kg/m2/s",
        "description": "ZM convection updraft mass flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZT_CLUBB": {
        "standard_name": "air_temperature",
        "cesm_name": "ZT_CLUBB",
        "units": "m",
        "description": "Thermodynamic Heights",
        "domain": "atmosphere",
        "component": "std"
    },
    "artm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "artm",
        "units": "degree_Celsius",
        "description": "annual mean air temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "smb": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "smb",
        "units": "mm/year water equivalent",
        "description": "surface mass balance",
        "domain": "atmosphere",
        "component": "std"
    },
    "thk": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "thk",
        "units": "meter",
        "description": "ice thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "topg": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "topg",
        "units": "meter",
        "description": "bedrock topography",
        "domain": "atmosphere",
        "component": "std"
    },
    "usurf": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "usurf",
        "units": "meter",
        "description": "ice upper surface elevation",
        "domain": "atmosphere",
        "component": "std"
    },
    "congel_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "congel_d",
        "units": "cm/day",
        "description": "congelation ice growth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "daidtd_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "daidtd_d",
        "units": "%/day",
        "description": "area tendency dynamics",
        "domain": "atmosphere",
        "component": "moar"
    },
    "daidtt_d": {
        "standard_name": "air_temperature",
        "cesm_name": "daidtt_d",
        "units": "%/day",
        "description": "area tendency thermo",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dvidtd_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dvidtd_d",
        "units": "cm/day",
        "description": "volume tendency dynamics",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dvidtt_d": {
        "standard_name": "air_temperature",
        "cesm_name": "dvidtt_d",
        "units": "cm/day",
        "description": "volume tendency thermo",
        "domain": "atmosphere",
        "component": "moar"
    },
    "frazil_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "frazil_d",
        "units": "cm/day",
        "description": "frazil ice growth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fswabs_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswabs_d",
        "units": "W/m2",
        "description": "snow/ice/ocn absorbed solar flux (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fswdn_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswdn_d",
        "units": "W/m2",
        "description": "down solar flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fswup_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswup_d",
        "units": "W/m2",
        "description": "upward solar flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FYarea_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FYarea_d",
        "units": "m2",
        "description": "first-year ice area",
        "domain": "atmosphere",
        "component": "moar"
    },
    "hs_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "hs_d",
        "units": "m",
        "description": "grid cell mean snow thickness",
        "domain": "atmosphere",
        "component": "moar"
    },
    "meltb_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "meltb_d",
        "units": "cm/day",
        "description": "basal ice melt",
        "domain": "atmosphere",
        "component": "moar"
    },
    "meltl_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "meltl_d",
        "units": "cm/day",
        "description": "lateral ice melt",
        "domain": "atmosphere",
        "component": "moar"
    },
    "melts_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "melts_d",
        "units": "cm/day",
        "description": "top snow melt",
        "domain": "atmosphere",
        "component": "moar"
    },
    "meltt_d": {
        "standard_name": "air_temperature",
        "cesm_name": "meltt_d",
        "units": "cm/day",
        "description": "top ice melt",
        "domain": "atmosphere",
        "component": "moar"
    },
    "rain_d": {
        "standard_name": "precipitation_flux",
        "cesm_name": "rain_d",
        "units": "cm/day",
        "description": "rainfall rate (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "snoice_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "snoice_d",
        "units": "cm/day",
        "description": "snow-ice formation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "snow_d": {
        "standard_name": "snowfall_flux",
        "cesm_name": "snow_d",
        "units": "cm/day",
        "description": "snowfall rate (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "snowfrac_d": {
        "standard_name": "snowfall_flux",
        "cesm_name": "snowfrac_d",
        "units": "1",
        "description": "grid cell mean snow fraction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strairx_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strairx_d",
        "units": "N/m2",
        "description": "atm/ice stress (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strairy_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strairy_d",
        "units": "N/m2",
        "description": "atm/ice stress (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strintx_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strintx_d",
        "units": "N/m2",
        "description": "internal ice stress (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strinty_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strinty_d",
        "units": "N/m2",
        "description": "internal ice stress (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strocnx_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strocnx_d",
        "units": "N/m2",
        "description": "ocean/ice stress (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strocny_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strocny_d",
        "units": "N/m2",
        "description": "ocean/ice stress (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "vicen_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "vicen_d",
        "units": "m",
        "description": "ice volume categories",
        "domain": "atmosphere",
        "component": "moar"
    },
    "vsnon_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "vsnon_d",
        "units": "m",
        "description": "snow depth on ice categories",
        "domain": "atmosphere",
        "component": "moar"
    },
    "divu": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "divu",
        "units": "%/day",
        "description": "strain rate (divergence)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fhocn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fhocn",
        "units": "W/m2",
        "description": "heat flux ice to ocn (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "flat_ai": {
        "standard_name": "air_temperature",
        "cesm_name": "flat_ai",
        "units": "W/m2",
        "description": "latent heat flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "flat": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "flat",
        "units": "W/m2",
        "description": "latent heat flux (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "flwdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "flwdn",
        "units": "W/m2",
        "description": "down longwave flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "flwup": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "flwup",
        "units": "W/m2",
        "description": "upward longwave flux (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fsens_ai": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fsens_ai",
        "units": "W/m2",
        "description": "sensible heat flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fsens": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fsens",
        "units": "W/m2",
        "description": "sensible heat flux (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fswabs": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswabs",
        "units": "W/m2",
        "description": "snow/ice/ocn absorbed solar flux (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fswintn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswintn",
        "units": "W m-2",
        "description": "internal absorbed shortwave categories",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fswsfcn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswsfcn",
        "units": "W m-2",
        "description": "surface absorbed shortwave categories",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fswthrun": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswthrun",
        "units": "W m-2",
        "description": "penetrating shortwave categories",
        "domain": "atmosphere",
        "component": "moar"
    },
    "fswup": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswup",
        "units": "W/m2",
        "description": "upward solar flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FYarea": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FYarea",
        "units": "m2",
        "description": "first-year ice area",
        "domain": "atmosphere",
        "component": "moar"
    },
    "melts": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "melts",
        "units": "cm/day",
        "description": "top snow melt",
        "domain": "atmosphere",
        "component": "moar"
    },
    "rain": {
        "standard_name": "precipitation_flux",
        "cesm_name": "rain",
        "units": "cm/day",
        "description": "rainfall rate (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "shear": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "shear",
        "units": "%/day",
        "description": "strain rate (shear)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "sig1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sig1",
        "units": "1",
        "description": "norm. principal stress 1",
        "domain": "atmosphere",
        "component": "moar"
    },
    "sig2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sig2",
        "units": "1",
        "description": "norm. principal stress 2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "snoice": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "snoice",
        "units": "cm/day",
        "description": "snow-ice formation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "snow": {
        "standard_name": "snowfall_flux",
        "cesm_name": "snow",
        "units": "cm/day",
        "description": "snowfall rate (cpl)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strairx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strairx",
        "units": "N/m2",
        "description": "atm/ice stress (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strairy": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strairy",
        "units": "N/m2",
        "description": "atm/ice stress (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strcorx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strcorx",
        "units": "N/m2",
        "description": "coriolis stress (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strcory": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strcory",
        "units": "N/m2",
        "description": "coriolis stress (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strength": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strength",
        "units": "N/m",
        "description": "compressive ice strength",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strintx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strintx",
        "units": "N/m2",
        "description": "internal ice stress (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strinty": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strinty",
        "units": "N/m2",
        "description": "internal ice stress (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strocnx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strocnx",
        "units": "N/m2",
        "description": "ocean/ice stress (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strocny": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strocny",
        "units": "N/m2",
        "description": "ocean/ice stress (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strtltx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strtltx",
        "units": "N/m2",
        "description": "sea sfc tilt stress (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "strtlty": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "strtlty",
        "units": "N/m2",
        "description": "sea sfc tilt stress (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Tsfc": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Tsfc",
        "units": "Celsius",
        "description": "snow/ice surface temperature",
        "domain": "atmosphere",
        "component": "moar"
    },
    "uvel": {
        "standard_name": "eastward_wind",
        "cesm_name": "uvel",
        "units": "m/s",
        "description": "ice velocity (x)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "vicen": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "vicen",
        "units": "m",
        "description": "ice volume categories",
        "domain": "atmosphere",
        "component": "moar"
    },
    "vsnon": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "vsnon",
        "units": "m",
        "description": "snow depth on ice categories",
        "domain": "atmosphere",
        "component": "moar"
    },
    "vvel": {
        "standard_name": "northward_wind",
        "cesm_name": "vvel",
        "units": "m/s",
        "description": "ice velocity (y)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "aice_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "aice_d",
        "units": "1",
        "description": "ice area (aggregate)",
        "domain": "atmosphere",
        "component": "std"
    },
    "aicen_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "aicen_d",
        "units": "1",
        "description": "ice area categories",
        "domain": "atmosphere",
        "component": "std"
    },
    "apond_ai_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "apond_ai_d",
        "units": "1",
        "description": "melt pond fraction of grid cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "fswthru_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswthru_d",
        "units": "W/m2",
        "description": "SW thru ice to ocean (cpl)",
        "domain": "atmosphere",
        "component": "std"
    },
    "hi_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "hi_d",
        "units": "m",
        "description": "grid cell mean ice thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "ice_present_d": {
        "standard_name": "air_temperature",
        "cesm_name": "ice_present_d",
        "units": "1",
        "description": "fraction of time-avg interval that ice is present",
        "domain": "atmosphere",
        "component": "std"
    },
    "sisnthick_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sisnthick_d",
        "units": "m",
        "description": "sea ice snow thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "sispeed_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sispeed_d",
        "units": "m/s",
        "description": "ice speed",
        "domain": "atmosphere",
        "component": "std"
    },
    "sitemptop_d": {
        "standard_name": "air_temperature",
        "cesm_name": "sitemptop_d",
        "units": "K",
        "description": "sea ice surface temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "sithick_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sithick_d",
        "units": "m",
        "description": "sea ice thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "siu_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siu_d",
        "units": "m/s",
        "description": "ice x velocity component",
        "domain": "atmosphere",
        "component": "std"
    },
    "siv_d": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siv_d",
        "units": "m/s",
        "description": "ice y velocity component",
        "domain": "atmosphere",
        "component": "std"
    },
    "aicen": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "aicen",
        "units": "1",
        "description": "ice area categories",
        "domain": "atmosphere",
        "component": "std"
    },
    "aice": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "aice",
        "units": "1",
        "description": "ice area (aggregate)",
        "domain": "atmosphere",
        "component": "std"
    },
    "albsni": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "albsni",
        "units": "%",
        "description": "snow/ice broad band albedo",
        "domain": "atmosphere",
        "component": "std"
    },
    "alidf_ai": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "alidf_ai",
        "units": "%",
        "description": "near IR diffuse albedo",
        "domain": "atmosphere",
        "component": "std"
    },
    "alidr_ai": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "alidr_ai",
        "units": "%",
        "description": "near IR direct albedo",
        "domain": "atmosphere",
        "component": "std"
    },
    "alvdf_ai": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "alvdf_ai",
        "units": "%",
        "description": "visible diffuse albedo",
        "domain": "atmosphere",
        "component": "std"
    },
    "alvdr_ai": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "alvdr_ai",
        "units": "%",
        "description": "visible direct albedo",
        "domain": "atmosphere",
        "component": "std"
    },
    "apeff_ai": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "apeff_ai",
        "units": "1",
        "description": "radiation-effective pond area fraction over grid cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "apond_ai": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "apond_ai",
        "units": "1",
        "description": "melt pond fraction of grid cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "ardg": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ardg",
        "units": "1",
        "description": "ridged ice area fraction",
        "domain": "atmosphere",
        "component": "std"
    },
    "congel": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "congel",
        "units": "cm/day",
        "description": "congelation ice growth",
        "domain": "atmosphere",
        "component": "std"
    },
    "dagedtd": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dagedtd",
        "units": "day/day",
        "description": "age tendency dynamics",
        "domain": "atmosphere",
        "component": "std"
    },
    "dagedtt": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dagedtt",
        "units": "day/day",
        "description": "age tendency thermo",
        "domain": "atmosphere",
        "component": "std"
    },
    "daidtd": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "daidtd",
        "units": "%/day",
        "description": "area tendency dynamics",
        "domain": "atmosphere",
        "component": "std"
    },
    "daidtt": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "daidtt",
        "units": "%/day",
        "description": "area tendency thermo",
        "domain": "atmosphere",
        "component": "std"
    },
    "dvidtd": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dvidtd",
        "units": "cm/day",
        "description": "volume tendency dynamics",
        "domain": "atmosphere",
        "component": "std"
    },
    "dvidtt": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dvidtt",
        "units": "cm/day",
        "description": "volume tendency thermo",
        "domain": "atmosphere",
        "component": "std"
    },
    "evap": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "evap",
        "units": "cm/day",
        "description": "evaporative water flux (cpl)",
        "domain": "atmosphere",
        "component": "std"
    },
    "frazil": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "frazil",
        "units": "cm/day",
        "description": "frazil ice growth",
        "domain": "atmosphere",
        "component": "std"
    },
    "fresh": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fresh",
        "units": "cm/day",
        "description": "freshwtr flx ice to ocn (cpl)",
        "domain": "atmosphere",
        "component": "std"
    },
    "fsalt": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fsalt",
        "units": "kg/m2/day",
        "description": "salt flux ice to ocn (cpl)",
        "domain": "atmosphere",
        "component": "std"
    },
    "fswdn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswdn",
        "units": "W/m2",
        "description": "down solar flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "fswthru": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "fswthru",
        "units": "W/m2",
        "description": "SW thru ice to ocean (cpl)",
        "domain": "atmosphere",
        "component": "std"
    },
    "hi": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "hi",
        "units": "m",
        "description": "grid cell mean ice thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "hs": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "hs",
        "units": "m",
        "description": "grid cell mean snow thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "ice_present": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ice_present",
        "units": "1",
        "description": "fraction of time-avg interval that ice is present",
        "domain": "atmosphere",
        "component": "std"
    },
    "meltb": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "meltb",
        "units": "cm/day",
        "description": "basal ice melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "meltl": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "meltl",
        "units": "cm/day",
        "description": "lateral ice melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "meltt": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "meltt",
        "units": "cm/day",
        "description": "top ice melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "siage": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siage",
        "units": "s",
        "description": "sea ice age",
        "domain": "atmosphere",
        "component": "std"
    },
    "sialb": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sialb",
        "units": "1",
        "description": "sea ice albedo",
        "domain": "atmosphere",
        "component": "std"
    },
    "sicompstren": {
        "standard_name": "air_pressure",
        "cesm_name": "sicompstren",
        "units": "N m-1",
        "description": "compressive sea ice strength",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidconcdyn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidconcdyn",
        "units": "1/s",
        "description": "sea ice area change from dynamics",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidconcth": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidconcth",
        "units": "1/s",
        "description": "sea ice area change from thermodynamics",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmassdyn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmassdyn",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change from dynamics",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmassevapsubl": {
        "standard_name": "air_pressure",
        "cesm_name": "sidmassevapsubl",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change from evaporation and sublimation",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmassgrowthbot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmassgrowthbot",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change from basal growth",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmassgrowthwat": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmassgrowthwat",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change from frazil",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmasslat": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmasslat",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change lateral melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmassmeltbot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmassmeltbot",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change bottom melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmassmelttop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmassmelttop",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change top melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmasssi": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmasssi",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change from snow-ice formation",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmassth": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmassth",
        "units": "kg m-2 s-1",
        "description": "sea ice mass change from thermodynamics",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmasstranx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmasstranx",
        "units": "kg/s",
        "description": "x component of snow and sea ice mass transport",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidmasstrany": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidmasstrany",
        "units": "kg/s",
        "description": "y component of snow and sea ice mass transport",
        "domain": "atmosphere",
        "component": "std"
    },
    "sidragtop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sidragtop",
        "units": "1",
        "description": "atmospheric drag over sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sifb": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sifb",
        "units": "m",
        "description": "sea ice freeboard above sea level",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflcondbot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflcondbot",
        "units": "W/m2",
        "description": "conductive heat flux at bottom of sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflcondtop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflcondtop",
        "units": "W/m2",
        "description": "conductive heat flux at top of sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflfwbot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflfwbot",
        "units": "kg m-2 s-1",
        "description": "fresh water flux from sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflfwdrain": {
        "standard_name": "precipitation_flux",
        "cesm_name": "siflfwdrain",
        "units": "kg m-2 s-1",
        "description": "fresh water drainage through sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sifllatstop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sifllatstop",
        "units": "W/m2",
        "description": "latent heat flux over sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sifllwdtop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sifllwdtop",
        "units": "W/m2",
        "description": "down longwave flux over sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sifllwutop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sifllwutop",
        "units": "W/m2",
        "description": "upward longwave flux over sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflsaltbot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflsaltbot",
        "units": "kg m-2 s-1",
        "description": "salt flux from sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflsenstop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflsenstop",
        "units": "W/m2",
        "description": "sensible heat flux over sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflsensupbot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflsensupbot",
        "units": "W/m2",
        "description": "sensible heat flux at bottom of sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflswdbot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflswdbot",
        "units": "W/m2",
        "description": "down shortwave flux at bottom of ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflswdtop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflswdtop",
        "units": "W/m2",
        "description": "down shortwave flux over sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siflswutop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siflswutop",
        "units": "W/m2",
        "description": "upward shortwave flux over sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "siforcecoriolx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siforcecoriolx",
        "units": "N m-2",
        "description": "coriolis term",
        "domain": "atmosphere",
        "component": "std"
    },
    "siforcecorioly": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siforcecorioly",
        "units": "N m-2",
        "description": "coriolis term",
        "domain": "atmosphere",
        "component": "std"
    },
    "siforceintstrx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siforceintstrx",
        "units": "N m-2",
        "description": "internal stress term",
        "domain": "atmosphere",
        "component": "std"
    },
    "siforceintstry": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siforceintstry",
        "units": "N m-2",
        "description": "internal stress term",
        "domain": "atmosphere",
        "component": "std"
    },
    "siforcetiltx": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siforcetiltx",
        "units": "N m-2",
        "description": "sea surface tilt term",
        "domain": "atmosphere",
        "component": "std"
    },
    "siforcetilty": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siforcetilty",
        "units": "N m-2",
        "description": "sea surface tile term",
        "domain": "atmosphere",
        "component": "std"
    },
    "sihc": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sihc",
        "units": "J m-2",
        "description": "sea ice heat content",
        "domain": "atmosphere",
        "component": "std"
    },
    "siitdconc": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siitdconc",
        "units": "1",
        "description": "ice area categories",
        "domain": "atmosphere",
        "component": "std"
    },
    "siitdsnthick": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siitdsnthick",
        "units": "m",
        "description": "snow thickness categories",
        "domain": "atmosphere",
        "component": "std"
    },
    "siitdthick": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siitdthick",
        "units": "m",
        "description": "ice thickness categories",
        "domain": "atmosphere",
        "component": "std"
    },
    "sipr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sipr",
        "units": "kg m-2 s-1",
        "description": "rainfall over sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sirdgthick": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sirdgthick",
        "units": "m",
        "description": "sea ice ridge thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "sisnhc": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sisnhc",
        "units": "J m-2",
        "description": "snow heat content",
        "domain": "atmosphere",
        "component": "std"
    },
    "sisnthick": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sisnthick",
        "units": "m",
        "description": "sea ice snow thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "sispeed": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sispeed",
        "units": "m/s",
        "description": "ice speed",
        "domain": "atmosphere",
        "component": "std"
    },
    "sistreave": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sistreave",
        "units": "N m-1",
        "description": "average normal stress",
        "domain": "atmosphere",
        "component": "std"
    },
    "sistremax": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sistremax",
        "units": "N m-1",
        "description": "maximum shear stress",
        "domain": "atmosphere",
        "component": "std"
    },
    "sistrxdtop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sistrxdtop",
        "units": "N m-2",
        "description": "x component of atmospheric stress on sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sistrxubot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sistrxubot",
        "units": "N m-2",
        "description": "x component of ocean stress on sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sistrydtop": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sistrydtop",
        "units": "N m-2",
        "description": "y component of atmospheric stress on sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sistryubot": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sistryubot",
        "units": "N m-2",
        "description": "y component of ocean stress on sea ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "sitempbot": {
        "standard_name": "air_temperature",
        "cesm_name": "sitempbot",
        "units": "K",
        "description": "sea ice bottom temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "sitempsnic": {
        "standard_name": "air_temperature",
        "cesm_name": "sitempsnic",
        "units": "K",
        "description": "snow ice interface temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "sitemptop": {
        "standard_name": "air_temperature",
        "cesm_name": "sitemptop",
        "units": "K",
        "description": "sea ice surface temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "sithick": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sithick",
        "units": "m",
        "description": "sea ice thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "siu": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siu",
        "units": "m/s",
        "description": "ice x velocity component",
        "domain": "atmosphere",
        "component": "std"
    },
    "siv": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "siv",
        "units": "m/s",
        "description": "ice y velocity component",
        "domain": "atmosphere",
        "component": "std"
    },
    "sndmassmelt": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sndmassmelt",
        "units": "kg m-2 s-1",
        "description": "snow mass change from snow melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "sndmasssnf": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sndmasssnf",
        "units": "kg m-2 s-1",
        "description": "snow mass change from snow fall",
        "domain": "atmosphere",
        "component": "std"
    },
    "sndmassubl": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sndmassubl",
        "units": "kg m-2 s-1",
        "description": "snow mass change from evaporation and sublimation",
        "domain": "atmosphere",
        "component": "std"
    },
    "snowfrac": {
        "standard_name": "snowfall_flux",
        "cesm_name": "snowfrac",
        "units": "1",
        "description": "grid cell mean snow fraction",
        "domain": "atmosphere",
        "component": "std"
    },
    "uatm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "uatm",
        "units": "m/s",
        "description": "atm velocity (x)",
        "domain": "atmosphere",
        "component": "std"
    },
    "vatm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "vatm",
        "units": "m/s",
        "description": "atm velocity (y)",
        "domain": "atmosphere",
        "component": "std"
    },
    "ALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ALT",
        "units": "m",
        "description": "current active layer thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "AR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AR",
        "units": "gC/m^2/s",
        "description": "autotrophic respiration (MR+GR)",
        "domain": "atmosphere",
        "component": "std"
    },
    "EFLX_LH_TOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EFLX_LH_TOT",
        "units": "W/m^2",
        "description": "total latent heat flux (+ to atm)",
        "domain": "atmosphere",
        "component": "std"
    },
    "FGR12": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FGR12",
        "units": "W/m^2",
        "description": "heat flux between soil layers 1 and 2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FIRA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FIRA",
        "units": "W/m^2",
        "description": "net infrared (longwave) radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSA",
        "units": "W/m^2",
        "description": "absorbed solar radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSDSND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDSND",
        "units": "W/m^2",
        "description": "direct nir incident solar radiation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSDSNI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDSNI",
        "units": "W/m^2",
        "description": "diffuse nir incident solar radiation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSDSVD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDSVD",
        "units": "W/m^2",
        "description": "direct vis incident solar radiation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSDSVI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDSVI",
        "units": "W/m^2",
        "description": "diffuse vis incident solar radiation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSH",
        "units": "W/m^2",
        "description": "sensible heat not including correction for land use change and rain/snow conversion",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSM",
        "units": "W/m^2",
        "description": "snow melt heat flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSNO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNO",
        "units": "unitless",
        "description": "fraction of ground covered by snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "GPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GPP",
        "units": "gC/m^2/s",
        "description": "gross primary production",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2OCAN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2OCAN",
        "units": "mm",
        "description": "intercepted water",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2OSFC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2OSFC",
        "units": "mm",
        "description": "surface water depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2OSNO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2OSNO",
        "units": "mm",
        "description": "snow depth (liquid water)",
        "domain": "atmosphere",
        "component": "std"
    },
    "HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HR",
        "units": "gC/m^2/s",
        "description": "total heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP",
        "units": "gC/m^2/s",
        "description": "net primary production",
        "domain": "atmosphere",
        "component": "std"
    },
    "QDRAI_PERCH": {
        "standard_name": "specific_humidity",
        "cesm_name": "QDRAI_PERCH",
        "units": "mm/s",
        "description": "perched wt drainage",
        "domain": "atmosphere",
        "component": "std"
    },
    "QDRAI": {
        "standard_name": "specific_humidity",
        "cesm_name": "QDRAI",
        "units": "mm/s",
        "description": "sub-surface drainage",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLX_SNOW_DRAIN": {
        "standard_name": "snowfall_flux",
        "cesm_name": "QFLX_SNOW_DRAIN",
        "units": "mm/s",
        "description": "drainage from snow pack",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLX_SUB_SNOW": {
        "standard_name": "snowfall_flux",
        "cesm_name": "QFLX_SUB_SNOW",
        "units": "mm H2O/s",
        "description": "sublimation rate from snow pack (also includes bare ice sublimation from glacier columns)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QINTR": {
        "standard_name": "specific_humidity",
        "cesm_name": "QINTR",
        "units": "mm/s",
        "description": "interception",
        "domain": "atmosphere",
        "component": "moar"
    },
    "QOVER": {
        "standard_name": "specific_humidity",
        "cesm_name": "QOVER",
        "units": "mm/s",
        "description": "surface runoff",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRUNOFF": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRUNOFF",
        "units": "mm/s",
        "description": "total liquid runoff not including correction for land use change",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNOEVAP": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSNOEVAP",
        "units": "mm/s",
        "description": "evaporation from snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNOFRZ": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSNOFRZ",
        "units": "kg/m2/s",
        "description": "column-integrated snow freezing rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSOIL": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSOIL",
        "units": "mm/s",
        "description": "Ground evaporation (soil/snow evaporation+soil/snow sublimation - dew)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QVEGE": {
        "standard_name": "specific_humidity",
        "cesm_name": "QVEGE",
        "units": "mm/s",
        "description": "canopy evaporation",
        "domain": "atmosphere",
        "component": "std"
    },
    "QVEGT": {
        "standard_name": "specific_humidity",
        "cesm_name": "QVEGT",
        "units": "mm/s",
        "description": "canopy transpiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "RAIN": {
        "standard_name": "precipitation_flux",
        "cesm_name": "RAIN",
        "units": "mm/s",
        "description": "atmospheric rain after rain/snow repartitioning based on temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOBCMSL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOBCMSL",
        "units": "kg/m2",
        "description": "mass of BC in top snow layer",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SNOCAN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOCAN",
        "units": "mm",
        "description": "intercepted snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOFSRND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOFSRND",
        "units": "W/m^2",
        "description": "direct nir reflected solar radiation from snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOFSRNI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOFSRNI",
        "units": "W/m^2",
        "description": "diffuse nir reflected solar radiation from snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOFSRVD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOFSRVD",
        "units": "W/m^2",
        "description": "direct vis reflected solar radiation from snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOFSRVI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOFSRVI",
        "units": "W/m^2",
        "description": "diffuse vis reflected solar radiation from snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOTXMASS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOTXMASS",
        "units": "K kg/m2",
        "description": "snow temperature times layer mass layer sum; to get mass-weighted temperature divide by (SNOWICE+SNOWLIQ)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOWDP": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOWDP",
        "units": "m",
        "description": "gridcell mean snow height",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOWICE": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOWICE",
        "units": "kg/m2",
        "description": "snow ice",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOWLIQ": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOWLIQ",
        "units": "kg/m2",
        "description": "snow liquid water",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOW": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOW",
        "units": "mm/s",
        "description": "atmospheric snow after rain/snow repartitioning based on temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOILICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOILICE",
        "units": "kg/m2",
        "description": "soil ice (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOILLIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "SOILLIQ",
        "units": "kg/m2",
        "description": "soil liquid water (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOILWATER_10CM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOILWATER_10CM",
        "units": "kg/m2",
        "description": "soil liquid water+ice in top 10cm of soil (veg landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TG": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TG",
        "units": "K",
        "description": "ground temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TLAI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TLAI",
        "units": "m^2/m^2",
        "description": "total projected leaf area index",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTSOILICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTSOILICE",
        "units": "kg/m2",
        "description": "vertically summed soil cie (veg landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTSOILLIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "TOTSOILLIQ",
        "units": "kg/m2",
        "description": "vertically summed soil liquid water (veg landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TREFMNAV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TREFMNAV",
        "units": "K",
        "description": "daily minimum of average 2-m temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TREFMXAV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TREFMXAV",
        "units": "K",
        "description": "daily maximum of average 2-m temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSKIN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSKIN",
        "units": "K",
        "description": "skin temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSOI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSOI",
        "units": "K",
        "description": "soil temperature (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TV",
        "units": "K",
        "description": "vegetation temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TWS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TWS",
        "units": "mm",
        "description": "total water storage",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_SOILC_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_SOILC_vr",
        "units": "gC14/m^3",
        "description": "C14 SOIL C (vertically resolved)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SOILC_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOILC_vr",
        "units": "gC/m^3",
        "description": "SOIL C (vertically resolved)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SOILN_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOILN_vr",
        "units": "gN/m^3",
        "description": "SOIL N (vertically resolved)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "RH2M": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RH2M",
        "units": "%",
        "description": "2m relative humidity",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSA",
        "units": "K",
        "description": "2m air temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "H2OSOI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2OSOI",
        "units": "mm3/mm3",
        "description": "volumetric soil water (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_NBP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_NBP",
        "units": "gC13/m^2/s",
        "description": "C13 net biome production includes fire landuse harvest and hrv_xsmrpool flux (latter smoothed over the year) positive for sink (same as net carbon exchange between land and atmosphere)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "C14_NBP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_NBP",
        "units": "gC13/m^2/s",
        "description": "C14 net biome production includes fire landuse harvest and hrv_xsmrpool flux (latter smoothed over the year) positive for sink (same as net carbon exchange between land and atmosphere)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DWT_SEEDN_TO_DEADSTEM": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_SEEDN_TO_DEADSTEM",
        "units": "gN/m^2/s",
        "description": "seed source to patch-level deadstem",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DWT_SEEDN_TO_LEAF": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_SEEDN_TO_LEAF",
        "units": "gN/m^2/s",
        "description": "seed source to patch-level leaf",
        "domain": "atmosphere",
        "component": "moar"
    },
    "EFLX_DYNBAL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EFLX_DYNBAL",
        "units": "W/m^2",
        "description": "dynamic land cover change conversion energy flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "EFLX_LH_TOT_R": {
        "standard_name": "air_temperature",
        "cesm_name": "EFLX_LH_TOT_R",
        "units": "W/m^2",
        "description": "Rural total evaporation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ERRH2OSNO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ERRH2OSNO",
        "units": "mm",
        "description": "imbalance in snow depth (liquid water)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ERRSEB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ERRSEB",
        "units": "W/m^2",
        "description": "surface energy conservation error",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ERRSOI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ERRSOI",
        "units": "W/m^2",
        "description": "soil/lake energy conservation error",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ERRSOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ERRSOL",
        "units": "W/m^2",
        "description": "solar radiation conservation error",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ESAI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ESAI",
        "units": "m^2/m^2",
        "description": "exposed one-sided stem area index",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FCOV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FCOV",
        "units": "unitless",
        "description": "fractional impermeable area",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FFIX_TO_SMINN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FFIX_TO_SMINN",
        "units": "gN/m^2/s",
        "description": "free living N fixation to soil mineral N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FGR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FGR",
        "units": "W/m^2",
        "description": "heat flux into soil/snow including snow melt and lake / snow light transmission",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FIRA_R": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FIRA_R",
        "units": "W/m^2",
        "description": "Rural net infrared (longwave) radiation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FPI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FPI",
        "units": "proportion",
        "description": "fraction of potential immobilization",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FROOTC_ALLOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FROOTC_ALLOC",
        "units": "gC/m^2/s",
        "description": "fine root C allocation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FROOTC_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FROOTC_LOSS",
        "units": "gC/m^2/s",
        "description": "fine root C loss",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FROOTC",
        "units": "gC/m^2",
        "description": "fine root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "FROOTN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FROOTN",
        "units": "gN/m^2",
        "description": "fine root N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSAT",
        "units": "unitless",
        "description": "fractional area with water table at surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSDSNDLN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDSNDLN",
        "units": "W/m^2",
        "description": "direct nir incident solar radiation at local noon",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSDSVDLN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDSVDLN",
        "units": "W/m^2",
        "description": "direct vis incident solar radiation at local noon",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSH_G": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSH_G",
        "units": "W/m^2",
        "description": "sensible heat from ground",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSH_R": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSH_R",
        "units": "W/m^2",
        "description": "Rural sensible heat",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSH_V": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSH_V",
        "units": "W/m^2",
        "description": "sensible heat from veg",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSRNDLN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSRNDLN",
        "units": "W/m^2",
        "description": "direct nir reflected solar radiation at local noon",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FSRVDLN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSRVDLN",
        "units": "W/m^2",
        "description": "direct vis reflected solar radiation at local noon",
        "domain": "atmosphere",
        "component": "moar"
    },
    "GROSS_NMIN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GROSS_NMIN",
        "units": "gN/m^2/s",
        "description": "gross rate of N mineralization",
        "domain": "atmosphere",
        "component": "moar"
    },
    "GR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GR",
        "units": "gC/m^2/s",
        "description": "total growth respiration",
        "domain": "atmosphere",
        "component": "moar"
    },
    "H2OSNO_TOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2OSNO_TOP",
        "units": "kg/m2",
        "description": "mass of snow in top snow layer",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HEAT_FROM_AC": {
        "standard_name": "air_temperature",
        "cesm_name": "HEAT_FROM_AC",
        "units": "W/m^2",
        "description": "sensible heat flux put into canyon due to heat removed from air conditioning",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HTOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HTOP",
        "units": "m",
        "description": "canopy top",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LAISHA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LAISHA",
        "units": "m^2/m^2",
        "description": "shaded projected leaf area index",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LAISUN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LAISUN",
        "units": "m^2/m^2",
        "description": "sunlit projected leaf area index",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LAND_USE_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LAND_USE_FLUX",
        "units": "gC/m^2/s",
        "description": "total C emitted from land cover conversion (smoothed over the year) and wood and grain product pools (NOTE: not a net value)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LEAFC_ALLOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFC_ALLOC",
        "units": "gC/m^2/s",
        "description": "leaf C allocation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LEAFC_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFC_LOSS",
        "units": "gC/m^2/s",
        "description": "leaf C loss",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LEAFC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFC",
        "units": "gC/m^2",
        "description": "leaf C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LEAFN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFN",
        "units": "gN/m^2",
        "description": "leaf N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITFALL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITFALL",
        "units": "gC/m^2/s",
        "description": "litterfall (leaves and fine roots)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITR1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR1C",
        "units": "gC/m^2",
        "description": "LITR1 C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITR1C_TO_SOIL1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR1C_TO_SOIL1C",
        "units": "gC/m^2/s",
        "description": "decomp. of litter 1 C to soil 1 C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITR1N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR1N",
        "units": "gN/m^2",
        "description": "LITR1 N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITR2C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR2C",
        "units": "gC/m^2",
        "description": "LITR2 C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITR2N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR2N",
        "units": "gN/m^2",
        "description": "LITR2 N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITR3C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR3C",
        "units": "gC/m^2",
        "description": "LITR3 C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITR3N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR3N",
        "units": "gN/m^2",
        "description": "LITR3 N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LITTERC_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITTERC_LOSS",
        "units": "gC/m^2/s",
        "description": "litter C loss",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LIVECROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LIVECROOTC",
        "units": "gC/m^2",
        "description": "live coarse root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "LIVECROOTN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LIVECROOTN",
        "units": "gN/m^2",
        "description": "live coarse root N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LIVESTEMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LIVESTEMC",
        "units": "gC/m^2",
        "description": "live stem C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "LIVESTEMN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LIVESTEMN",
        "units": "gN/m^2",
        "description": "live stem N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "MR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MR",
        "units": "gC/m^2/s",
        "description": "maintenance respiration",
        "domain": "atmosphere",
        "component": "moar"
    },
    "NDEPLOY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NDEPLOY",
        "units": "gN/m^2/s",
        "description": "total N deployed in new growth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "NDEP_TO_SMINN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NDEP_TO_SMINN",
        "units": "gN/m^2/s",
        "description": "atmospheric N deposition to soil mineral N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "NET_NMIN": {
        "standard_name": "air_temperature",
        "cesm_name": "NET_NMIN",
        "units": "gN/m^2/s",
        "description": "net rate of N mineralization",
        "domain": "atmosphere",
        "component": "moar"
    },
    "OCDEP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "OCDEP",
        "units": "kg/m^2/s",
        "description": "total OC deposition (dry+wet) from atmosphere",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PCO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PCO2",
        "units": "Pa",
        "description": "atmospheric partial pressure of CO2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PFT_FIRE_CLOSS": {
        "standard_name": "air_temperature",
        "cesm_name": "PFT_FIRE_CLOSS",
        "units": "gC/m^2/s",
        "description": "total patch-level fire C loss for non-peat fires outside land-type converted region",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PFT_FIRE_NLOSS": {
        "standard_name": "air_temperature",
        "cesm_name": "PFT_FIRE_NLOSS",
        "units": "gN/m^2/s",
        "description": "total patch-level fire N loss",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PLANT_NDEMAND": {
        "standard_name": "air_temperature",
        "cesm_name": "PLANT_NDEMAND",
        "units": "gN/m^2/s",
        "description": "N flux required to support initial GPP",
        "domain": "atmosphere",
        "component": "moar"
    },
    "POTENTIAL_IMMOB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POTENTIAL_IMMOB",
        "units": "gN/m^2/s",
        "description": "potential N immobilization",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PSNSHADE_TO_CPOOL": {
        "standard_name": "air_pressure",
        "cesm_name": "PSNSHADE_TO_CPOOL",
        "units": "gC/m^2/s",
        "description": "C fixation from shaded canopy",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PSNSHA": {
        "standard_name": "air_pressure",
        "cesm_name": "PSNSHA",
        "units": "umolCO2/m^2/s",
        "description": "shaded leaf photosynthesis",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PSNSUN": {
        "standard_name": "air_pressure",
        "cesm_name": "PSNSUN",
        "units": "umolCO2/m^2/s",
        "description": "sunlit leaf photosynthesis",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PSNSUN_TO_CPOOL": {
        "standard_name": "air_pressure",
        "cesm_name": "PSNSUN_TO_CPOOL",
        "units": "gC/m^2/s",
        "description": "C fixation from sunlit canopy",
        "domain": "atmosphere",
        "component": "moar"
    },
    "QDRIP": {
        "standard_name": "specific_humidity",
        "cesm_name": "QDRIP",
        "units": "mm/s",
        "description": "throughfall",
        "domain": "atmosphere",
        "component": "moar"
    },
    "QFLX_ICE_DYNBAL": {
        "standard_name": "specific_humidity",
        "cesm_name": "QFLX_ICE_DYNBAL",
        "units": "mm/s",
        "description": "ice dynamic land cover change conversion runoff flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "QFLX_LIQ_DYNBAL": {
        "standard_name": "specific_humidity",
        "cesm_name": "QFLX_LIQ_DYNBAL",
        "units": "mm/s",
        "description": "liq dynamic land cover change conversion runoff flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "QRUNOFF_RAIN_TO_SNOW_CONVERSION": {
        "standard_name": "convective_precipitation_flux",
        "cesm_name": "QRUNOFF_RAIN_TO_SNOW_CONVERSION",
        "units": "mm/s",
        "description": "liquid runoff from rain-to-snow conversion when this conversion leads to immediate runoff",
        "domain": "atmosphere",
        "component": "moar"
    },
    "RETRANSN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RETRANSN",
        "units": "gN/m^2",
        "description": "plant pool of retranslocated N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "RETRANSN_TO_NPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RETRANSN_TO_NPOOL",
        "units": "gN/m^2/s",
        "description": "deployment of retranslocated N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "RR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RR",
        "units": "gC/m^2/s",
        "description": "root respiration (fine root MR+total root GR)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SABG": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SABG",
        "units": "W/m^2",
        "description": "solar rad absorbed by ground",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SABV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SABV",
        "units": "W/m^2",
        "description": "solar rad absorbed by veg",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SEEDC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SEEDC",
        "units": "gC/m^2",
        "description": "pool for seeding new PFTs via dynamic landcover",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SEEDN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SEEDN",
        "units": "gN/m^2",
        "description": "pool for seeding new PFTs via dynamic landcover",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SMINN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SMINN",
        "units": "gN/m^2",
        "description": "soil mineral N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SMINN_TO_NPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SMINN_TO_NPOOL",
        "units": "gN/m^2/s",
        "description": "deployment of soil mineral N uptake",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SMINN_TO_PLANT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SMINN_TO_PLANT",
        "units": "gN/m^2/s",
        "description": "plant uptake of soil mineral N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SNOBCMCL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOBCMCL",
        "units": "kg/m2",
        "description": "mass of BC in snow column",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SNODSTMCL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNODSTMCL",
        "units": "kg/m2",
        "description": "mass of dust in snow column",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SNODSTMSL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNODSTMSL",
        "units": "kg/m2",
        "description": "mass of dust in top snow layer",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SNOOCMCL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOOCMCL",
        "units": "kg/m2",
        "description": "mass of OC in snow column",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SNOOCMSL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOOCMSL",
        "units": "kg/m2",
        "description": "mass of OC in top snow layer",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SNOW_SINKS": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOW_SINKS",
        "units": "mm/s",
        "description": "snow sinks (liquid water)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SOIL1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL1C",
        "units": "gC/m^2",
        "description": "SOIL1 C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SOIL1N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL1N",
        "units": "gN/m^2",
        "description": "SOIL1 N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SOIL2C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL2C",
        "units": "gC/m^2",
        "description": "SOIL2 C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SOIL2N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL2N",
        "units": "gN/m^2",
        "description": "SOIL2 N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SOIL3C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL3C",
        "units": "gC/m^2",
        "description": "SOIL3 C",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SOIL3N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL3N",
        "units": "gN/m^2",
        "description": "SOIL3 N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SR",
        "units": "gC/m^2/s",
        "description": "total soil respiration (HR+root resp)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "STORVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STORVEGC",
        "units": "gC/m^2",
        "description": "stored vegetation carbon excluding cpool",
        "domain": "atmosphere",
        "component": "moar"
    },
    "STORVEGN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STORVEGN",
        "units": "gN/m^2",
        "description": "stored vegetation nitrogen",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SUPPLEMENT_TO_SMINN": {
        "standard_name": "air_temperature",
        "cesm_name": "SUPPLEMENT_TO_SMINN",
        "units": "gN/m^2/s",
        "description": "supplemental N supply",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TBUILD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TBUILD",
        "units": "K",
        "description": "internal urban building air temperature",
        "domain": "atmosphere",
        "component": "moar"
    },
    "THBOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "THBOT",
        "units": "K",
        "description": "atmospheric air potential temperature (downscaled to columns in glacier regions)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TOTCOLC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTCOLC",
        "units": "gC/m^2",
        "description": "total column carbon incl veg and cpool but excl product pools",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TOTCOLN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTCOLN",
        "units": "gN/m^2",
        "description": "total column-level N excluding product pools",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TOTLITC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTLITC",
        "units": "gC/m^2",
        "description": "total litter carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTLITN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTLITN",
        "units": "gN/m^2",
        "description": "total litter N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TOTPFTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTPFTC",
        "units": "gC/m^2",
        "description": "total patch-level carbon including cpool",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TOTPFTN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTPFTN",
        "units": "gN/m^2",
        "description": "total patch-level nitrogen",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TOTSOMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTSOMC",
        "units": "gC/m^2",
        "description": "total soil organic matter carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTSOMN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTSOMN",
        "units": "gN/m^2",
        "description": "total soil organic matter N",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TSAI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSAI",
        "units": "m^2/m^2",
        "description": "total projected stem area index",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TSOI_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSOI_ICE",
        "units": "K",
        "description": "soil temperature (ice landunits only)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "URBAN_AC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "URBAN_AC",
        "units": "W/m^2",
        "description": "urban air conditioning flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "URBAN_HEAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "URBAN_HEAT",
        "units": "W/m^2",
        "description": "urban heating flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WASTEHEAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WASTEHEAT",
        "units": "W/m^2",
        "description": "sensible heat flux from heating/cooling sources of urban waste heat",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WOODC_ALLOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WOODC_ALLOC",
        "units": "gC/m^2/s",
        "description": "wood C eallocation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WOODC_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WOODC_LOSS",
        "units": "gC/m^2/s",
        "description": "wood C loss",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WOODC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WOODC",
        "units": "gC/m^2",
        "description": "wood C",
        "domain": "atmosphere",
        "component": "std"
    },
    "WOOD_HARVESTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WOOD_HARVESTC",
        "units": "gC/m^2/s",
        "description": "wood harvest carbon (to product pools)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WOOD_HARVESTN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WOOD_HARVESTN",
        "units": "gN/m^2/s",
        "description": "wood harvest N (to product pools)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "XSMRPOOL_RECOVER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "XSMRPOOL_RECOVER",
        "units": "gC/m^2/s",
        "description": "C flux assigned to recovery of negative xsmrpool",
        "domain": "atmosphere",
        "component": "moar"
    },
    "XSMRPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "XSMRPOOL",
        "units": "gC/m^2",
        "description": "temporary photosynthate C pool",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ZBOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ZBOT",
        "units": "m",
        "description": "atmospheric reference height",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CPHASE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CPHASE",
        "units": "0-not planted 1-planted 2-leaf emerge 3-grain fill 4-harvest",
        "description": "crop phenology phase",
        "domain": "atmosphere",
        "component": "std"
    },
    "CROPPROD1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CROPPROD1C",
        "units": "gC/m^2",
        "description": "1-yr grain product C",
        "domain": "atmosphere",
        "component": "std"
    },
    "CWDC_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CWDC_vr",
        "units": "gC/m^3",
        "description": "CWD C (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CWDN_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CWDN_vr",
        "units": "gN/m^3",
        "description": "CWD N (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "DEADCROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DEADCROOTC",
        "units": "gC/m^2",
        "description": "dead coarse root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNO_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNO_ICE",
        "units": "unitless",
        "description": "fraction of ground covered by snow (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR1C_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR1C_vr",
        "units": "gC/m^3",
        "description": "LITR1 C (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR1N_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR1N_vr",
        "units": "gN/m^3",
        "description": "LITR1 N (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR2C_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR2C_vr",
        "units": "gC/m^3",
        "description": "LITR2 C (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR2N_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR2N_vr",
        "units": "gN/m^3",
        "description": "LITR2 N (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR3C_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR3C_vr",
        "units": "gC/m^3",
        "description": "LITR3 C (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR3N_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR3N_vr",
        "units": "gN/m^3",
        "description": "LITR3 N (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PCT_CFT": {
        "standard_name": "air_temperature",
        "cesm_name": "PCT_CFT",
        "units": "%",
        "description": "% of each crop on the crop landunit",
        "domain": "atmosphere",
        "component": "std"
    },
    "PCT_GLC_MEC": {
        "standard_name": "air_temperature",
        "cesm_name": "PCT_GLC_MEC",
        "units": "%",
        "description": "% of each GLC elevation class on the glc_mec landunit",
        "domain": "atmosphere",
        "component": "std"
    },
    "PCT_LANDUNIT": {
        "standard_name": "air_temperature",
        "cesm_name": "PCT_LANDUNIT",
        "units": "%",
        "description": "% of each landunit on grid cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "PCT_NAT_PFT": {
        "standard_name": "air_temperature",
        "cesm_name": "PCT_NAT_PFT",
        "units": "%",
        "description": "% of each PFT on the natural vegetation (i.e. soil) landunit",
        "domain": "atmosphere",
        "component": "std"
    },
    "QICE_FORC": {
        "standard_name": "specific_humidity",
        "cesm_name": "QICE_FORC",
        "units": "mm/s",
        "description": "qice forcing sent to GLC",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOIL1C_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL1C_vr",
        "units": "gC/m^3",
        "description": "SOIL1 C (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOIL1N_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL1N_vr",
        "units": "gN/m^3",
        "description": "SOIL1 N (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOIL2C_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL2C_vr",
        "units": "gC/m^3",
        "description": "SOIL2 C (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOIL2N_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL2N_vr",
        "units": "gN/m^3",
        "description": "SOIL2 N (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOIL3C_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL3C_vr",
        "units": "gC/m^3",
        "description": "SOIL3 C (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOIL3N_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOIL3N_vr",
        "units": "gN/m^3",
        "description": "SOIL3 N (vertically resolved)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOPO_FORC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOPO_FORC",
        "units": "m",
        "description": "topograephic height sent to GLC",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTECOSYSC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTECOSYSC",
        "units": "gC/m^2",
        "description": "total ecosystem carbon incl veg but excl cpool and product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTSOMC_1m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTSOMC_1m",
        "units": "gC/m^2",
        "description": "total soil organic matter carbon to 1 meter depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTVEGC",
        "units": "gC/m^2",
        "description": "total vegetation carbon excluding cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOT_WOODPRODC": {
        "standard_name": "air_temperature",
        "cesm_name": "TOT_WOODPRODC",
        "units": "gC/m^2",
        "description": "total wood product C",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSRF_FORC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSRF_FORC",
        "units": "K",
        "description": "surface temperature sent to GLC",
        "domain": "atmosphere",
        "component": "std"
    },
    "ACTUAL_IMMOB": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ACTUAL_IMMOB",
        "units": "gN/m^2/s",
        "description": "actual N immobilization",
        "domain": "atmosphere",
        "component": "std"
    },
    "AGNPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AGNPP",
        "units": "gC/m^2/s",
        "description": "aboveground NPP",
        "domain": "atmosphere",
        "component": "std"
    },
    "ALTMAX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ALTMAX",
        "units": "m",
        "description": "maximum annual active layer thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "ATM_TOPO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ATM_TOPO",
        "units": "m",
        "description": "atmospheric surface height",
        "domain": "atmosphere",
        "component": "std"
    },
    "BAF_CROP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BAF_CROP",
        "units": "proportion/sec",
        "description": "fractional area burned for crop",
        "domain": "atmosphere",
        "component": "std"
    },
    "BAF_PEATF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BAF_PEATF",
        "units": "proportion/sec",
        "description": "fractional area burned in peatland",
        "domain": "atmosphere",
        "component": "std"
    },
    "BCDEP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BCDEP",
        "units": "kg/m^2/s",
        "description": "total BC deposition (dry+wet) from atmosphere",
        "domain": "atmosphere",
        "component": "std"
    },
    "BGNPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BGNPP",
        "units": "gC/m^2/s",
        "description": "belowground NPP",
        "domain": "atmosphere",
        "component": "std"
    },
    "BTRAN2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BTRAN2",
        "units": "unitless",
        "description": "root zone soil wetness factor",
        "domain": "atmosphere",
        "component": "std"
    },
    "BTRANMN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BTRANMN",
        "units": "unitless",
        "description": "daily minimum of transpiration beta factor",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_AGNPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_AGNPP",
        "units": "gC13/m^2/s",
        "description": "C13 aboveground NPP",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_AR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_AR",
        "units": "gC13/m^2/s",
        "description": "C13 autotrophic respiration (MR+GR)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_BGNPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_BGNPP",
        "units": "gC13/m^2/s",
        "description": "C13 belowground NPP",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_COL_FIRE_CLOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_COL_FIRE_CLOSS",
        "units": "gC13/m^2/s",
        "description": "C13 total column-level fire C loss",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_CPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_CPOOL",
        "units": "gC13/m^2",
        "description": "C13 temporary photosynthate C pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_CROPPROD1C_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_CROPPROD1C_LOSS",
        "units": "gC13/m^2/s",
        "description": "loss from 1-yr grain product pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_CROPPROD1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_CROPPROD1C",
        "units": "gC13/m^2",
        "description": "1-yr grain product C13",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_CROPSEEDC_DEFICIT": {
        "standard_name": "air_pressure",
        "cesm_name": "C13_CROPSEEDC_DEFICIT",
        "units": "gC/m^2",
        "description": "C13 C used for crop seed that needs to be repaid",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_CWDC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_CWDC",
        "units": "gC13/m^2",
        "description": "C13 CWD C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_DEADCROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_DEADCROOTC",
        "units": "gC13/m^2",
        "description": "C13 dead coarse root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_DEADSTEMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_DEADSTEMC",
        "units": "gC13/m^2",
        "description": "C13 dead stem C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_DISPVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_DISPVEGC",
        "units": "gC13/m^2",
        "description": "C13 displayed veg carbon excluding storage and cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_DWT_CONV_CFLUX_DRIBBLED": {
        "standard_name": "air_temperature",
        "cesm_name": "C13_DWT_CONV_CFLUX_DRIBBLED",
        "units": "gC13/m^2/s",
        "description": "C13 conversion C flux (immediate loss to atm) dribbled throughout the year",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_DWT_CONV_CFLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "C13_DWT_CONV_CFLUX",
        "units": "gC13/m^2/s",
        "description": "C13 conversion C flux (immediate loss to atm) (0 at all times except first timestep of year)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_DWT_CROPPROD1C_GAIN": {
        "standard_name": "air_temperature",
        "cesm_name": "C13_DWT_CROPPROD1C_GAIN",
        "units": "gC13/m^2/s",
        "description": "landcover change-driven addition to 1-year crop product pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_DWT_SLASH_CFLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "C13_DWT_SLASH_CFLUX",
        "units": "gC/m^2/s",
        "description": "C13 slash C flux to litter and CWD due to land use",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_DWT_WOODPRODC_GAIN": {
        "standard_name": "air_temperature",
        "cesm_name": "C13_DWT_WOODPRODC_GAIN",
        "units": "gC13/m^2/s",
        "description": "landcover change-driven addition to wood product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_ER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_ER",
        "units": "gC13/m^2/s",
        "description": "C13 total ecosystem respiration autotrophic+heterotrophic",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_FROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_FROOTC",
        "units": "gC13/m^2",
        "description": "C13 fine root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_GPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_GPP",
        "units": "gC13/m^2/s",
        "description": "C13 gross primary production",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_GRAINC": {
        "standard_name": "precipitation_flux",
        "cesm_name": "C13_GRAINC",
        "units": "gC/m^2",
        "description": "C13 grain C (does not equal yield)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_GR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_GR",
        "units": "gC13/m^2/s",
        "description": "C13 total growth respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_HR",
        "units": "gC13/m^2/s",
        "description": "C13 total heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_LEAFC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_LEAFC",
        "units": "gC13/m^2",
        "description": "C13 leaf C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_LITR1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_LITR1C",
        "units": "gC13/m^2",
        "description": "C13 LITR1 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_LITR2C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_LITR2C",
        "units": "gC13/m^2",
        "description": "C13 LITR2 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_LITR3C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_LITR3C",
        "units": "gC13/m^2",
        "description": "C13 LITR3 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_LITTERC_HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_LITTERC_HR",
        "units": "gC13/m^2/s",
        "description": "C13 fine root C litterfall to litter 3 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_LIVECROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_LIVECROOTC",
        "units": "gC13/m^2",
        "description": "C13 live coarse root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_LIVESTEMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_LIVESTEMC",
        "units": "gC13/m^2",
        "description": "C13 live stem C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_MR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_MR",
        "units": "gC13/m^2/s",
        "description": "C13 maintenance respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_NEE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_NEE",
        "units": "gC13/m^2/s",
        "description": "C13 net ecosystem exchange of carbon includes fire flux positive for source",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_NEP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_NEP",
        "units": "gC13/m^2/s",
        "description": "C13 net ecosystem production excludes fire flux positive for sink",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_NPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_NPP",
        "units": "gC13/m^2/s",
        "description": "C13 net primary production",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_PFT_FIRE_CLOSS": {
        "standard_name": "air_temperature",
        "cesm_name": "C13_PFT_FIRE_CLOSS",
        "units": "gC13/m^2/s",
        "description": "C13 total patch-level fire C loss",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_PSNSHADE_TO_CPOOL": {
        "standard_name": "air_pressure",
        "cesm_name": "C13_PSNSHADE_TO_CPOOL",
        "units": "gC13/m^2/s",
        "description": "C13 C fixation from shaded canopy",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_PSNSHA": {
        "standard_name": "air_pressure",
        "cesm_name": "C13_PSNSHA",
        "units": "umolCO2/m^2/s",
        "description": "C13 shaded leaf photosynthesis",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_PSNSUN": {
        "standard_name": "air_pressure",
        "cesm_name": "C13_PSNSUN",
        "units": "umolCO2/m^2/s",
        "description": "C13 sunlit leaf photosynthesis",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_PSNSUN_TO_CPOOL": {
        "standard_name": "air_pressure",
        "cesm_name": "C13_PSNSUN_TO_CPOOL",
        "units": "gC13/m^2/s",
        "description": "C13 C fixation from sunlit canopy",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_RR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_RR",
        "units": "gC13/m^2/s",
        "description": "C13 root respiration (fine root MR+total root GR)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_SEEDC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_SEEDC",
        "units": "gC13/m^2",
        "description": "C13 pool for seeding new PFTs via dynamic landcover",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_SOIL1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_SOIL1C",
        "units": "gC13/m^2",
        "description": "C13 SOIL1 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_SOIL2C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_SOIL2C",
        "units": "gC13/m^2",
        "description": "C13 SOIL2 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_SOIL3C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_SOIL3C",
        "units": "gC13/m^2",
        "description": "C13 SOIL3 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_SOILC_HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_SOILC_HR",
        "units": "gC13/m^2/s",
        "description": "C13 soil organic matter heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_SR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_SR",
        "units": "gC13/m^2/s",
        "description": "C13 total soil respiration (HR+root resp)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_STORVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_STORVEGC",
        "units": "gC13/m^2",
        "description": "C13 stored vegetation carbon excluding cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOTCOLC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_TOTCOLC",
        "units": "gC13/m^2",
        "description": "C13 total column carbon incl veg and cpool but excl product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOTECOSYSC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_TOTECOSYSC",
        "units": "gC13/m^2",
        "description": "C13 total ecosystem carbon incl veg but excl cpool and product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOTLITC_1m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_TOTLITC_1m",
        "units": "gC13/m^2",
        "description": "C13 total litter carbon to 1 meter",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOTLITC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_TOTLITC",
        "units": "gC13/m^2",
        "description": "C13 total litter carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOTPFTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_TOTPFTC",
        "units": "gC13/m^2",
        "description": "C13 total patch-level carbon including cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOTSOMC_1m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_TOTSOMC_1m",
        "units": "gC13/m^2",
        "description": "C13 total soil organic matter carbon to 1 meter",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOTSOMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_TOTSOMC",
        "units": "gC13/m^2",
        "description": "C13 total soil organic matter carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOTVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_TOTVEGC",
        "units": "gC13/m^2",
        "description": "C13 total vegetation carbon excluding cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOT_WOODPRODC_LOSS": {
        "standard_name": "air_temperature",
        "cesm_name": "C13_TOT_WOODPRODC_LOSS",
        "units": "gC13/m^2/s",
        "description": "total loss from wood product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_TOT_WOODPRODC": {
        "standard_name": "air_temperature",
        "cesm_name": "C13_TOT_WOODPRODC",
        "units": "gC13/m^2",
        "description": "total wood product C13",
        "domain": "atmosphere",
        "component": "std"
    },
    "C13_XSMRPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C13_XSMRPOOL",
        "units": "gC13/m^2",
        "description": "C13 temporary photosynthate C pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_AGNPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_AGNPP",
        "units": "gC14/m^2/s",
        "description": "C14 aboveground NPP",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_AR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_AR",
        "units": "gC14/m^2/s",
        "description": "C14 autotrophic respiration (MR+GR)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_BGNPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_BGNPP",
        "units": "gC14/m^2/s",
        "description": "C14 belowground NPP",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_COL_FIRE_CLOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_COL_FIRE_CLOSS",
        "units": "gC14/m^2/s",
        "description": "C14 total column-level fire C loss",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_CPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_CPOOL",
        "units": "gC14/m^2",
        "description": "C14 temporary photosynthate C pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_CROPPROD1C_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_CROPPROD1C_LOSS",
        "units": "gC14/m^2/s",
        "description": "loss from 1-yr grain product pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_CROPPROD1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_CROPPROD1C",
        "units": "gC14/m^2",
        "description": "1-yr grain product C14",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_CROPSEEDC_DEFICIT": {
        "standard_name": "air_pressure",
        "cesm_name": "C14_CROPSEEDC_DEFICIT",
        "units": "gC/m^2",
        "description": "C14 C used for crop seed that needs to be repaid",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_CWDC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_CWDC",
        "units": "gC14/m^2",
        "description": "C14 CWD C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_DEADCROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_DEADCROOTC",
        "units": "gC14/m^2",
        "description": "C14 dead coarse root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_DEADSTEMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_DEADSTEMC",
        "units": "gC14/m^2",
        "description": "C14 dead stem C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_DISPVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_DISPVEGC",
        "units": "gC14/m^2",
        "description": "C14 displayed veg carbon excluding storage and cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_DWT_CONV_CFLUX_DRIBBLED": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_DWT_CONV_CFLUX_DRIBBLED",
        "units": "gC14/m^2/s",
        "description": "C14 conversion C flux (immediate loss to atm) dribbled throughout the year",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_DWT_CONV_CFLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_DWT_CONV_CFLUX",
        "units": "gC14/m^2/s",
        "description": "C14 conversion C flux (immediate loss to atm) (0 at all times except first timestep of year)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_DWT_CROPPROD1C_GAIN": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_DWT_CROPPROD1C_GAIN",
        "units": "gC14/m^2/s",
        "description": "landcover change-driven addition to 1-year crop product pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_DWT_SLASH_CFLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_DWT_SLASH_CFLUX",
        "units": "gC/m^2/s",
        "description": "C14 slash C flux to litter and CWD due to land use",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_DWT_WOODPRODC_GAIN": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_DWT_WOODPRODC_GAIN",
        "units": "gC14/m^2/s",
        "description": "landcover change-driven addition to wood product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_ER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_ER",
        "units": "gC14/m^2/s",
        "description": "C14 total ecosystem respiration autotrophic+heterotrophic",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_FROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_FROOTC",
        "units": "gC14/m^2",
        "description": "C14 fine root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_GPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_GPP",
        "units": "gC14/m^2/s",
        "description": "C14 gross primary production",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_GRAINC": {
        "standard_name": "precipitation_flux",
        "cesm_name": "C14_GRAINC",
        "units": "gC/m^2",
        "description": "C14 grain C (does not equal yield)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_GR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_GR",
        "units": "gC14/m^2/s",
        "description": "C14 total growth respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_HR",
        "units": "gC14/m^2/s",
        "description": "C14 total heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_LEAFC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_LEAFC",
        "units": "gC14/m^2",
        "description": "C14 leaf C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_LITR1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_LITR1C",
        "units": "gC14/m^2",
        "description": "C14 LITR1 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_LITR2C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_LITR2C",
        "units": "gC14/m^2",
        "description": "C14 LITR2 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_LITR3C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_LITR3C",
        "units": "gC14/m^2",
        "description": "C14 LITR3 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_LITTERC_HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_LITTERC_HR",
        "units": "gC14/m^2/s",
        "description": "C14 litter carbon heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_LIVECROOTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_LIVECROOTC",
        "units": "gC14/m^2",
        "description": "C14 live coarse root C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_LIVESTEMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_LIVESTEMC",
        "units": "gC14/m^2",
        "description": "C14 live stem C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_MR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_MR",
        "units": "gC14/m^2/s",
        "description": "C14 maintenance respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_NEE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_NEE",
        "units": "gC14/m^2/s",
        "description": "C14 net ecosystem exchange of carbon includes fire flux positive for source",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_NEP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_NEP",
        "units": "gC14/m^2/s",
        "description": "C14 net ecosystem production excludes fire flux positive for sink",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_NPP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_NPP",
        "units": "gC14/m^2/s",
        "description": "C14 net primary production",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_PFT_CTRUNC": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_PFT_CTRUNC",
        "units": "gC14/m^2",
        "description": "C14 patch-level sink for C truncation",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_PFT_FIRE_CLOSS": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_PFT_FIRE_CLOSS",
        "units": "gC14/m^2/s",
        "description": "C14 total patch-level fire C loss",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_PSNSHADE_TO_CPOOL": {
        "standard_name": "air_pressure",
        "cesm_name": "C14_PSNSHADE_TO_CPOOL",
        "units": "gC14/m^2/s",
        "description": "C14 C fixation from shaded canopy",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_PSNSHA": {
        "standard_name": "air_pressure",
        "cesm_name": "C14_PSNSHA",
        "units": "umolCO2/m^2/s",
        "description": "C14 shaded leaf photosynthesis",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_PSNSUN": {
        "standard_name": "air_pressure",
        "cesm_name": "C14_PSNSUN",
        "units": "umolCO2/m^2/s",
        "description": "C14 sunlit leaf photosynthesis",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_PSNSUN_TO_CPOOL": {
        "standard_name": "air_pressure",
        "cesm_name": "C14_PSNSUN_TO_CPOOL",
        "units": "gC14/m^2/s",
        "description": "C14 C fixation from sunlit canopy",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_RR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_RR",
        "units": "gC14/m^2/s",
        "description": "C14 root respiration (fine root MR+total root GR)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_SEEDC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_SEEDC",
        "units": "gC14/m^2",
        "description": "C14 pool for seeding new PFTs via dynamic landcover",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_SOIL1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_SOIL1C",
        "units": "gC14/m^2",
        "description": "C14 SOIL1 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_SOIL2C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_SOIL2C",
        "units": "gC14/m^2",
        "description": "C14 SOIL2 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_SOIL3C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_SOIL3C",
        "units": "gC14/m^2",
        "description": "C14 SOIL3 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_SOILC_HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_SOILC_HR",
        "units": "gC14/m^2/s",
        "description": "C14 soil organic matter heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_SR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_SR",
        "units": "gC14/m^2/s",
        "description": "C14 total soil respiration (HR+root resp)",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_STORVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_STORVEGC",
        "units": "gC14/m^2",
        "description": "C14 stored vegetation carbon excluding cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOTCOLC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_TOTCOLC",
        "units": "gC14/m^2",
        "description": "C14 total column carbon incl veg and cpool but excl product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOTECOSYSC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_TOTECOSYSC",
        "units": "gC14/m^2",
        "description": "C14 total ecosystem carbon incl veg but excl cpool and product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOTLITC_1m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_TOTLITC_1m",
        "units": "gC14/m^2",
        "description": "C14 total litter carbon to 1 meter",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOTLITC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_TOTLITC",
        "units": "gC14/m^2",
        "description": "C14 total litter carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOTPFTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_TOTPFTC",
        "units": "gC14/m^2",
        "description": "C14 total patch-level carbon including cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOTSOMC_1m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_TOTSOMC_1m",
        "units": "gC14/m^2",
        "description": "C14 total soil organic matter carbon to 1 meter",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOTSOMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_TOTSOMC",
        "units": "gC14/m^2",
        "description": "C14 total soil organic matter carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOTVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_TOTVEGC",
        "units": "gC14/m^2",
        "description": "C14 total vegetation carbon excluding cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOT_WOODPRODC_LOSS": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_TOT_WOODPRODC_LOSS",
        "units": "gC14/m^2/s",
        "description": "total loss from wood product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_TOT_WOODPRODC": {
        "standard_name": "air_temperature",
        "cesm_name": "C14_TOT_WOODPRODC",
        "units": "gC14/m^2",
        "description": "total wood product C14",
        "domain": "atmosphere",
        "component": "std"
    },
    "C14_XSMRPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "C14_XSMRPOOL",
        "units": "gC14/m^2",
        "description": "C14 temporary photosynthate C pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "CH4PROD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CH4PROD",
        "units": "gC/m2/s",
        "description": "Gridcell total production of CH4",
        "domain": "atmosphere",
        "component": "std"
    },
    "CH4_SURF_AERE_SAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CH4_SURF_AERE_SAT",
        "units": "mol/m2/s",
        "description": "aerenchyma surface CH4 flux for inundated area; (+ to atm)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CH4_SURF_AERE_UNSAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CH4_SURF_AERE_UNSAT",
        "units": "mol/m2/s",
        "description": "aerenchyma surface CH4 flux for non-inundated area; (+ to atm)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CH4_SURF_DIFF_SAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CH4_SURF_DIFF_SAT",
        "units": "mol/m2/s",
        "description": "diffusive surface CH4 flux for inundated / lake area; (+ to atm)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CH4_SURF_DIFF_UNSAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CH4_SURF_DIFF_UNSAT",
        "units": "mol/m2/s",
        "description": "diffusive surface CH4 flux for non-inundated area; (+ to atm)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CH4_SURF_EBUL_SAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CH4_SURF_EBUL_SAT",
        "units": "mol/m2/s",
        "description": "ebullition surface CH4 flux for inundated / lake area; (+ to atm)",
        "domain": "atmosphere",
        "component": "std"
    },
    "CH4_SURF_EBUL_UNSAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CH4_SURF_EBUL_UNSAT",
        "units": "mol/m2/s",
        "description": "ebullition surface CH4 flux for non-inundated area; (+ to atm)",
        "domain": "atmosphere",
        "component": "std"
    },
    "COL_FIRE_CLOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "COL_FIRE_CLOSS",
        "units": "gC/m^2/s",
        "description": "total column-level fire C loss for non-peat fires outside land-type converted region",
        "domain": "atmosphere",
        "component": "std"
    },
    "COL_FIRE_NLOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "COL_FIRE_NLOSS",
        "units": "gN/m^2/s",
        "description": "total column-level fire N loss",
        "domain": "atmosphere",
        "component": "std"
    },
    "COST_NACTIVE": {
        "standard_name": "air_temperature",
        "cesm_name": "COST_NACTIVE",
        "units": "gN/gC",
        "description": "Cost of active uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "COST_NFIX": {
        "standard_name": "air_temperature",
        "cesm_name": "COST_NFIX",
        "units": "gN/gC",
        "description": "Cost of fixation",
        "domain": "atmosphere",
        "component": "std"
    },
    "COST_NRETRANS": {
        "standard_name": "air_temperature",
        "cesm_name": "COST_NRETRANS",
        "units": "gN/gC",
        "description": "Cost of retranslocation",
        "domain": "atmosphere",
        "component": "std"
    },
    "CPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CPOOL",
        "units": "gC/m^2",
        "description": "temporary photosynthate C pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "CROPPROD1C_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CROPPROD1C_LOSS",
        "units": "gC/m^2/s",
        "description": "loss from 1-yr grain product pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "CROPPROD1N_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CROPPROD1N_LOSS",
        "units": "gN/m^2/s",
        "description": "loss from 1-yr grain product pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "CROPPROD1N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CROPPROD1N",
        "units": "gN/m^2",
        "description": "1-yr grain product N",
        "domain": "atmosphere",
        "component": "std"
    },
    "CROPSEEDC_DEFICIT": {
        "standard_name": "air_pressure",
        "cesm_name": "CROPSEEDC_DEFICIT",
        "units": "gC/m^2",
        "description": "C used for crop seed that needs to be repaid",
        "domain": "atmosphere",
        "component": "std"
    },
    "CWDC_LOSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CWDC_LOSS",
        "units": "gC/m^2/s",
        "description": "coarse woody debris C loss",
        "domain": "atmosphere",
        "component": "std"
    },
    "CWDC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CWDC",
        "units": "gC/m^2",
        "description": "CWD C",
        "domain": "atmosphere",
        "component": "std"
    },
    "CWDN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CWDN",
        "units": "gN/m^2",
        "description": "CWD N",
        "domain": "atmosphere",
        "component": "std"
    },
    "DEADCROOTN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DEADCROOTN",
        "units": "gN/m^2",
        "description": "dead coarse root N",
        "domain": "atmosphere",
        "component": "std"
    },
    "DEADSTEMC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DEADSTEMC",
        "units": "gC/m^2",
        "description": "dead stem C",
        "domain": "atmosphere",
        "component": "std"
    },
    "DEADSTEMN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DEADSTEMN",
        "units": "gN/m^2",
        "description": "dead stem N",
        "domain": "atmosphere",
        "component": "std"
    },
    "DENIT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DENIT",
        "units": "gN/m^2/s",
        "description": "total rate of denitrification",
        "domain": "atmosphere",
        "component": "std"
    },
    "DISPVEGC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DISPVEGC",
        "units": "gC/m^2",
        "description": "displayed veg carbon excluding storage and cpool",
        "domain": "atmosphere",
        "component": "std"
    },
    "DISPVEGN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DISPVEGN",
        "units": "gN/m^2",
        "description": "displayed vegetation nitrogen",
        "domain": "atmosphere",
        "component": "std"
    },
    "DSL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DSL",
        "units": "mm",
        "description": "dry surface layer thickness",
        "domain": "atmosphere",
        "component": "std"
    },
    "DSTDEP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DSTDEP",
        "units": "kg/m^2/s",
        "description": "total dust deposition (dry+wet) from atmosphere",
        "domain": "atmosphere",
        "component": "std"
    },
    "DSTFLXT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DSTFLXT",
        "units": "kg/m2/s",
        "description": "total surface dust emission",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_CONV_CFLUX_DRIBBLED": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_CONV_CFLUX_DRIBBLED",
        "units": "gC/m^2/s",
        "description": "conversion C flux (immediate loss to atm) dribbled throughout the year",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_CONV_CFLUX_PATCH": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_CONV_CFLUX_PATCH",
        "units": "gC/m^2/s",
        "description": "patch-level conversion C flux (immediate loss to atm) (0 at all times except first timestep of year) (per-area-gridcell; only makes sense with dov2xy=.false.)",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_CONV_CFLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_CONV_CFLUX",
        "units": "gC/m^2/s",
        "description": "conversion C flux (immediate loss to atm) (0 at all times except first timestep of year)",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_CONV_NFLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_CONV_NFLUX",
        "units": "gN/m^2/s",
        "description": "conversion N flux (immediate loss to atm) (0 at all times except first timestep of year)",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_CROPPROD1C_GAIN": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_CROPPROD1C_GAIN",
        "units": "gC/m^2/s",
        "description": "landcover change-driven addition to 1-year crop product pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_CROPPROD1N_GAIN": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_CROPPROD1N_GAIN",
        "units": "gN/m^2/s",
        "description": "landcover change-driven addition to 1-year crop product pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_SLASH_CFLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_SLASH_CFLUX",
        "units": "gC/m^2/s",
        "description": "slash C flux to litter and CWD due to land use",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_WOODPRODC_GAIN": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_WOODPRODC_GAIN",
        "units": "gC/m^2/s",
        "description": "landcover change-driven addition to wood product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_WOODPRODN_GAIN": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_WOODPRODN_GAIN",
        "units": "gN/m^2/s",
        "description": "landcover change-driven addition to wood product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "DWT_WOOD_PRODUCTC_GAIN_PATCH": {
        "standard_name": "air_temperature",
        "cesm_name": "DWT_WOOD_PRODUCTC_GAIN_PATCH",
        "units": "gC/m^2/s",
        "description": "patch-level landcover change-driven addition to wood product pools(0 at all times except first timestep of year) (per-area-gridcell; only makes sense with dov2xy=.false.)",
        "domain": "atmosphere",
        "component": "std"
    },
    "EFLXBUILD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EFLXBUILD",
        "units": "W/m^2",
        "description": "building heat flux from change in interior building air temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "EFLX_GRND_LAKE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EFLX_GRND_LAKE",
        "units": "W/m^2",
        "description": "net heat flux into lake/snow surface excluding light transmission",
        "domain": "atmosphere",
        "component": "std"
    },
    "EFLX_LH_TOT_ICE": {
        "standard_name": "air_temperature",
        "cesm_name": "EFLX_LH_TOT_ICE",
        "units": "W/m^2",
        "description": "total latent heat flux (+ to atm) (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "ELAI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ELAI",
        "units": "m^2/m^2",
        "description": "exposed one-sided leaf area index",
        "domain": "atmosphere",
        "component": "std"
    },
    "ERRH2O": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ERRH2O",
        "units": "mm",
        "description": "total water conservation error",
        "domain": "atmosphere",
        "component": "std"
    },
    "ER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ER",
        "units": "gC/m^2/s",
        "description": "total ecosystem respiration autotrophic+heterotrophic",
        "domain": "atmosphere",
        "component": "std"
    },
    "FAREA_BURNED": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FAREA_BURNED",
        "units": "proportion/sec",
        "description": "timestep fractional area burned",
        "domain": "atmosphere",
        "component": "std"
    },
    "FCEV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FCEV",
        "units": "W/m^2",
        "description": "canopy evaporation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FCH4_DFSAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FCH4_DFSAT",
        "units": "kgC/m2/s",
        "description": "CH4 additional flux due to changing fsat vegetated landunits only",
        "domain": "atmosphere",
        "component": "std"
    },
    "FCH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FCH4",
        "units": "kgC/m2/s",
        "description": "Gridcell surface CH4 flux to atmosphere (+ to atm)",
        "domain": "atmosphere",
        "component": "std"
    },
    "FCH4TOCO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FCH4TOCO2",
        "units": "gC/m2/s",
        "description": "Gridcell oxidation of CH4 to CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "FCTR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FCTR",
        "units": "W/m^2",
        "description": "canopy transpiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "F_DENIT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "F_DENIT",
        "units": "gN/m^2/s",
        "description": "denitrification flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "FGEV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FGEV",
        "units": "W/m^2",
        "description": "ground evaporation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FH2OSFC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FH2OSFC",
        "units": "unitless",
        "description": "fraction of ground covered by surface water",
        "domain": "atmosphere",
        "component": "std"
    },
    "FINUNDATED": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FINUNDATED",
        "units": "unitless",
        "description": "fractional inundated area of vegetated columns",
        "domain": "atmosphere",
        "component": "std"
    },
    "FIRE_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FIRE_ICE",
        "units": "W/m^2",
        "description": "emitted infrared (longwave) radiation (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "FIRE_R": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FIRE_R",
        "units": "W/m^2",
        "description": "Rural emitted infrared (longwave) radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FIRE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FIRE",
        "units": "W/m^2",
        "description": "emitted infrared (longwave) radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FLDS_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FLDS_ICE",
        "units": "W/m^2",
        "description": "atmospheric longwave radiation (downscaled to columns in glacier regions) (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "F_N2O_DENIT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "F_N2O_DENIT",
        "units": "gN/m^2/s",
        "description": "denitrification N2O flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "F_N2O_NIT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "F_N2O_NIT",
        "units": "gN/m^2/s",
        "description": "nitrification N2O flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "F_NIT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "F_NIT",
        "units": "gN/m^2/s",
        "description": "nitrification flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "FPSN": {
        "standard_name": "air_pressure",
        "cesm_name": "FPSN",
        "units": "umol/m2s",
        "description": "photosynthesis",
        "domain": "atmosphere",
        "component": "std"
    },
    "FREE_RETRANSN_TO_NPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FREE_RETRANSN_TO_NPOOL",
        "units": "gN/m^2/s",
        "description": "deployment of retranslocated N",
        "domain": "atmosphere",
        "component": "std"
    },
    "FROOTC_TO_LITTER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FROOTC_TO_LITTER",
        "units": "gC/m^2/s",
        "description": "fine root C litterfall",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSDSVILN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSDSVILN",
        "units": "W/m^2",
        "description": "diffuse vis incident solar radiation at local noon",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSH_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSH_ICE",
        "units": "W/m^2",
        "description": "sensible heat not including correction for land use change and rain/snow conversion (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSH_PRECIP_CONVERSION": {
        "standard_name": "convective_precipitation_flux",
        "cesm_name": "FSH_PRECIP_CONVERSION",
        "units": "W/m^2",
        "description": "Sensible heat flux from conversion of rain/snow atm forcing",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSH_RUNOFF_ICE_TO_LIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "FSH_RUNOFF_ICE_TO_LIQ",
        "units": "W/m^2",
        "description": "sensible heat flux generated from conversion of ice runoff to liquid",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSH_TO_COUPLER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSH_TO_COUPLER",
        "units": "W/m^2",
        "description": "sensible heat sent to coupler (includes corrections for land use change rain/snow conversion and conversion of ice runoff to liquid)",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSNO_EFF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSNO_EFF",
        "units": "unitless",
        "description": "effective fraction of ground covered by snow",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSR_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSR_ICE",
        "units": "W/m^2",
        "description": "reflected solar radiation (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSRND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSRND",
        "units": "W/m^2",
        "description": "direct nir reflected solar radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSRNI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSRNI",
        "units": "W/m^2",
        "description": "diffuse nir reflected solar radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSR",
        "units": "W/m^2",
        "description": "reflected solar radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSRVD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSRVD",
        "units": "W/m^2",
        "description": "direct vis reflected solar radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FSRVI": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FSRVI",
        "units": "W/m^2",
        "description": "diffuse vis reflected solar radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "FUELC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FUELC",
        "units": "gC/m^2",
        "description": "fuel load",
        "domain": "atmosphere",
        "component": "std"
    },
    "GRAINC": {
        "standard_name": "precipitation_flux",
        "cesm_name": "GRAINC",
        "units": "gC/m^2",
        "description": "grain C (does not equal yield)",
        "domain": "atmosphere",
        "component": "std"
    },
    "GRAINC_TO_FOOD": {
        "standard_name": "precipitation_flux",
        "cesm_name": "GRAINC_TO_FOOD",
        "units": "gC/m^2/s",
        "description": "grain C to food",
        "domain": "atmosphere",
        "component": "std"
    },
    "GRAINC_TO_SEED": {
        "standard_name": "precipitation_flux",
        "cesm_name": "GRAINC_TO_SEED",
        "units": "gC/m^2/s",
        "description": "grain C to seed",
        "domain": "atmosphere",
        "component": "std"
    },
    "GRAINN": {
        "standard_name": "precipitation_flux",
        "cesm_name": "GRAINN",
        "units": "gN/m^2",
        "description": "grain N",
        "domain": "atmosphere",
        "component": "std"
    },
    "GSSHALN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GSSHALN",
        "units": "umol H20/m2/s",
        "description": "shaded leaf stomatal conductance at local noon",
        "domain": "atmosphere",
        "component": "std"
    },
    "GSSHA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GSSHA",
        "units": "umol H20/m2/s",
        "description": "shaded leaf stomatal conductance",
        "domain": "atmosphere",
        "component": "std"
    },
    "GSSUNLN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GSSUNLN",
        "units": "umol H20/m2/s",
        "description": "sunlit leaf stomatal conductance at local noon",
        "domain": "atmosphere",
        "component": "std"
    },
    "GSSUN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GSSUN",
        "units": "umol H20/m2/s",
        "description": "sunlit leaf stomatal conductance",
        "domain": "atmosphere",
        "component": "std"
    },
    "HEAT_CONTENT1": {
        "standard_name": "air_temperature",
        "cesm_name": "HEAT_CONTENT1",
        "units": "J/m^2",
        "description": "initial gridcell total heat content",
        "domain": "atmosphere",
        "component": "std"
    },
    "HIA_R": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HIA_R",
        "units": "C",
        "description": "Rural 2 m NWS Heat Index",
        "domain": "atmosphere",
        "component": "std"
    },
    "HIA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HIA",
        "units": "C",
        "description": "2 m NWS Heat Index",
        "domain": "atmosphere",
        "component": "std"
    },
    "HIA_U": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HIA_U",
        "units": "C",
        "description": "Urban 2 m NWS Heat Index",
        "domain": "atmosphere",
        "component": "std"
    },
    "HR_vr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HR_vr",
        "units": "gC/m^3/s",
        "description": "total vertically resolved heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "HUMIDEX_R": {
        "standard_name": "specific_humidity",
        "cesm_name": "HUMIDEX_R",
        "units": "C",
        "description": "Rural 2 m Humidex",
        "domain": "atmosphere",
        "component": "std"
    },
    "HUMIDEX": {
        "standard_name": "specific_humidity",
        "cesm_name": "HUMIDEX",
        "units": "C",
        "description": "2 m Humidex",
        "domain": "atmosphere",
        "component": "std"
    },
    "HUMIDEX_U": {
        "standard_name": "specific_humidity",
        "cesm_name": "HUMIDEX_U",
        "units": "C",
        "description": "Urban 2 m Humidex",
        "domain": "atmosphere",
        "component": "std"
    },
    "ICE_CONTENT1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ICE_CONTENT1",
        "units": "mm",
        "description": "initial gridcell total ice content",
        "domain": "atmosphere",
        "component": "std"
    },
    "JMX25T": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "JMX25T",
        "units": "umol/m2/s",
        "description": "canopy profile of jmax",
        "domain": "atmosphere",
        "component": "std"
    },
    "Jmx25Z": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Jmx25Z",
        "units": "umol/m2/s",
        "description": "canopy profile of vcmax25 predicted by LUNA model",
        "domain": "atmosphere",
        "component": "std"
    },
    "LAKEICEFRAC_SURF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LAKEICEFRAC_SURF",
        "units": "unitless",
        "description": "surface lake layer ice mass fraction",
        "domain": "atmosphere",
        "component": "std"
    },
    "LAKEICETHICK": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LAKEICETHICK",
        "units": "m",
        "description": "thickness of lake ice (including physical expansion on freezing)",
        "domain": "atmosphere",
        "component": "std"
    },
    "LEAFC_CHANGE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFC_CHANGE",
        "units": "gC/m^2/s",
        "description": "C change in leaf",
        "domain": "atmosphere",
        "component": "std"
    },
    "LEAFCN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFCN",
        "units": "gC/gN",
        "description": "Leaf CN ratio used for flexible CN",
        "domain": "atmosphere",
        "component": "std"
    },
    "LEAFC_TO_LITTER_FUN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFC_TO_LITTER_FUN",
        "units": "gC/m^2/s",
        "description": "leaf C litterfall used by FUN",
        "domain": "atmosphere",
        "component": "std"
    },
    "LEAFC_TO_LITTER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFC_TO_LITTER",
        "units": "gC/m^2/s",
        "description": "leaf C litterfall",
        "domain": "atmosphere",
        "component": "std"
    },
    "LEAF_MR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAF_MR",
        "units": "gC/m^2/s",
        "description": "leaf maintenance respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "LEAFN_TO_LITTER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LEAFN_TO_LITTER",
        "units": "gN/m^2/s",
        "description": "leaf N litterfall",
        "domain": "atmosphere",
        "component": "std"
    },
    "LFC2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LFC2",
        "units": "per sec",
        "description": "conversion area fraction of BET and BDT that burned",
        "domain": "atmosphere",
        "component": "std"
    },
    "LIQCAN": {
        "standard_name": "specific_humidity",
        "cesm_name": "LIQCAN",
        "units": "mm",
        "description": "intercepted liquid water",
        "domain": "atmosphere",
        "component": "std"
    },
    "LIQUID_CONTENT1": {
        "standard_name": "specific_humidity",
        "cesm_name": "LIQUID_CONTENT1",
        "units": "mm",
        "description": "initial gridcell total liq content",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR1N_TO_SOIL1N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR1N_TO_SOIL1N",
        "units": "gN/m^2",
        "description": "decomp. of litter 1 N to soil 1 N",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR2C_TO_SOIL1C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR2C_TO_SOIL1C",
        "units": "gC/m^2/s",
        "description": "decomp. of litter 2 C to soil 1 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR2N_TO_SOIL1N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR2N_TO_SOIL1N",
        "units": "gN/m^2",
        "description": "decomp. of litter 2 N to soil 1 N",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR3C_TO_SOIL2C": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR3C_TO_SOIL2C",
        "units": "gC/m^2/s",
        "description": "decomp. of litter 3 C to soil 2 C",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITR3N_TO_SOIL2N": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITR3N_TO_SOIL2N",
        "units": "gN/m^2",
        "description": "decomp. of litter 3 N to soil 2 N",
        "domain": "atmosphere",
        "component": "std"
    },
    "LITTERC_HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LITTERC_HR",
        "units": "gC/m^2/s",
        "description": "litter C heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "LNC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LNC",
        "units": "gN leaf/m^2",
        "description": "leaf N concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "NACTIVE_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NACTIVE_NH4",
        "units": "gN/m^2/s",
        "description": "Mycorrhizal N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NACTIVE_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NACTIVE_NO3",
        "units": "gN/m^2/s",
        "description": "Mycorrhizal N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NACTIVE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NACTIVE",
        "units": "gN/m^2/s",
        "description": "Mycorrhizal N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NAM_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NAM_NH4",
        "units": "gN/m^2/s",
        "description": "AM-associated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NAM_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NAM_NO3",
        "units": "gN/m^2/s",
        "description": "AM-associated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NAM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NAM",
        "units": "gN/m^2/s",
        "description": "AM-associated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NBP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NBP",
        "units": "gC/m^2/s",
        "description": "net biome production includes fire landuse harvest and hrv_xsmrpool flux (latter smoothed over the year) positive for sink (same as net carbon exchange between land and atmosphere)",
        "domain": "atmosphere",
        "component": "std"
    },
    "NECM_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NECM_NH4",
        "units": "gN/m^2/s",
        "description": "ECM-associated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NECM_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NECM_NO3",
        "units": "gN/m^2/s",
        "description": "ECM-associated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NECM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NECM",
        "units": "gN/m^2/s",
        "description": "ECM-associated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NEE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NEE",
        "units": "gC/m^2/s",
        "description": "net ecosystem exchange of carbon includes fire and hrv_xsmrpool (latter smoothed over the year) excludes landuse and harvest flux positive for source",
        "domain": "atmosphere",
        "component": "std"
    },
    "NEM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NEM",
        "units": "gC/m2/s",
        "description": "Gridcell net adjustment to net carbon exchange passed to atm. for methane production",
        "domain": "atmosphere",
        "component": "std"
    },
    "NEP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NEP",
        "units": "gC/m^2/s",
        "description": "net ecosystem production excludes fire landuse and harvest flux positive for sink",
        "domain": "atmosphere",
        "component": "std"
    },
    "NFERTILIZATION": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NFERTILIZATION",
        "units": "gN/m^2/s",
        "description": "fertilizer added",
        "domain": "atmosphere",
        "component": "std"
    },
    "NFIRE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NFIRE",
        "units": "counts/km2/sec",
        "description": "fire counts valid only in Reg.C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NFIX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NFIX",
        "units": "gN/m^2/s",
        "description": "Symbiotic BNF uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NNONMYC_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NNONMYC_NH4",
        "units": "gN/m^2/s",
        "description": "Non-mycorrhizal N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NNONMYC_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NNONMYC_NO3",
        "units": "gN/m^2/s",
        "description": "Non-mycorrhizal N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NNONMYC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NNONMYC",
        "units": "gN/m^2/s",
        "description": "Non-mycorrhizal N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPASSIVE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPASSIVE",
        "units": "gN/m^2/s",
        "description": "Passive N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPOOL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPOOL",
        "units": "gN/m^2",
        "description": "temporary plant N pool",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_GROWTH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_GROWTH",
        "units": "gC/m^2/s",
        "description": "Total C used for growth in FUN",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NACTIVE_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NACTIVE_NH4",
        "units": "gC/m^2/s",
        "description": "Mycorrhizal N uptake use C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NACTIVE_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NACTIVE_NO3",
        "units": "gC/m^2/s",
        "description": "Mycorrhizal N uptake used C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NACTIVE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NACTIVE",
        "units": "gC/m^2/s",
        "description": "Mycorrhizal N uptake used C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NAM_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NAM_NH4",
        "units": "gC/m^2/s",
        "description": "AM-associated N uptake use C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NAM_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NAM_NO3",
        "units": "gC/m^2/s",
        "description": "AM-associated N uptake use C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NAM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NAM",
        "units": "gC/m^2/s",
        "description": "AM-associated N uptake used C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NECM_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NECM_NH4",
        "units": "gC/m^2/s",
        "description": "ECM-associated N uptake use C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NECM_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NECM_NO3",
        "units": "gC/m^2/s",
        "description": "ECM-associated N uptake used C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NECM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NECM",
        "units": "gC/m^2/s",
        "description": "ECM-associated N uptake used C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NFIX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NFIX",
        "units": "gC/m^2/s",
        "description": "Symbiotic BNF uptake used C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NNONMYC_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NNONMYC_NH4",
        "units": "gC/m^2/s",
        "description": "Non-mycorrhizal N uptake use C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NNONMYC_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NNONMYC_NO3",
        "units": "gC/m^2/s",
        "description": "Non-mycorrhizal N uptake use C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NNONMYC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NNONMYC",
        "units": "gC/m^2/s",
        "description": "Non-mycorrhizal N uptake used C",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NRETRANS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NRETRANS",
        "units": "gC/m^2/s",
        "description": "Retranslocated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NPP_NUPTAKE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NPP_NUPTAKE",
        "units": "gC/m^2/s",
        "description": "Total C used by N uptake in FUN",
        "domain": "atmosphere",
        "component": "std"
    },
    "NRETRANS_REG": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NRETRANS_REG",
        "units": "gN/m^2/s",
        "description": "Retranslocated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NRETRANS_SEASON": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NRETRANS_SEASON",
        "units": "gN/m^2/s",
        "description": "Retranslocated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NRETRANS_STRESS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NRETRANS_STRESS",
        "units": "gN/m^2/s",
        "description": "Retranslocated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NRETRANS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NRETRANS",
        "units": "gN/m^2/s",
        "description": "Retranslocated N uptake flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NUPTAKE_NPP_FRACTION": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NUPTAKE_NPP_FRACTION",
        "units": "no units",
        "description": "frac of NPP used in N uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "NUPTAKE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NUPTAKE",
        "units": "gN/m^2/s",
        "description": "Total N uptake of FUN",
        "domain": "atmosphere",
        "component": "std"
    },
    "O_SCALAR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "O_SCALAR",
        "units": "unitless",
        "description": "fraction by which decomposition is reduced due to anoxia",
        "domain": "atmosphere",
        "component": "std"
    },
    "PARVEGLN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PARVEGLN",
        "units": "W/m^2",
        "description": "absorbed par by vegetation at local noon",
        "domain": "atmosphere",
        "component": "std"
    },
    "PBOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PBOT",
        "units": "Pa",
        "description": "atmospheric pressure at surface (downscaled to columns in glacier regions)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PCH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PCH4",
        "units": "Pa",
        "description": "atmospheric partial pressure of CH4",
        "domain": "atmosphere",
        "component": "std"
    },
    "POT_F_DENIT": {
        "standard_name": "air_temperature",
        "cesm_name": "POT_F_DENIT",
        "units": "gN/m^2/s",
        "description": "potential denitrification flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "POT_F_NIT": {
        "standard_name": "air_temperature",
        "cesm_name": "POT_F_NIT",
        "units": "gN/m^2/s",
        "description": "potential nitrification flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "Q2M": {
        "standard_name": "specific_humidity",
        "cesm_name": "Q2M",
        "units": "kg/kg",
        "description": "2m specific humidity",
        "domain": "atmosphere",
        "component": "std"
    },
    "QBOT": {
        "standard_name": "specific_humidity",
        "cesm_name": "QBOT",
        "units": "kg/kg",
        "description": "atmospheric specific humidity (downscaled to columns in glacier regions)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QCHARGE": {
        "standard_name": "specific_humidity",
        "cesm_name": "QCHARGE",
        "units": "mm/s",
        "description": "aquifer recharge rate (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QDRAI_XS": {
        "standard_name": "specific_humidity",
        "cesm_name": "QDRAI_XS",
        "units": "mm/s",
        "description": "saturation excess drainage",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLOOD": {
        "standard_name": "specific_humidity",
        "cesm_name": "QFLOOD",
        "units": "mm/s",
        "description": "runoff from river flooding",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLX_DEW_GRND": {
        "standard_name": "specific_humidity",
        "cesm_name": "QFLX_DEW_GRND",
        "units": "mm H2O/s",
        "description": "ground surface dew formation",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLX_DEW_SNOW": {
        "standard_name": "snowfall_flux",
        "cesm_name": "QFLX_DEW_SNOW",
        "units": "mm H2O/s",
        "description": "surface dew added to snow pacK",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLX_EVAP_TOT": {
        "standard_name": "specific_humidity",
        "cesm_name": "QFLX_EVAP_TOT",
        "units": "mm H2O/s",
        "description": "qflx_evap_soi+qflx_evap_can+qflx_tran_veg",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLX_SNOW_DRAIN_ICE": {
        "standard_name": "snowfall_flux",
        "cesm_name": "QFLX_SNOW_DRAIN_ICE",
        "units": "mm/s",
        "description": "drainage from snow pack melt (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLX_SUB_SNOW_ICE": {
        "standard_name": "snowfall_flux",
        "cesm_name": "QFLX_SUB_SNOW_ICE",
        "units": "mm H2O/s",
        "description": "sublimation rate from snow pack (also includes bare ice sublimation from glacier columns) (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QH2OSFC": {
        "standard_name": "specific_humidity",
        "cesm_name": "QH2OSFC",
        "units": "mm/s",
        "description": "surface water runoff",
        "domain": "atmosphere",
        "component": "std"
    },
    "QICE_FRZ": {
        "standard_name": "specific_humidity",
        "cesm_name": "QICE_FRZ",
        "units": "mm/s",
        "description": "ice growth",
        "domain": "atmosphere",
        "component": "std"
    },
    "QICE_MELT": {
        "standard_name": "specific_humidity",
        "cesm_name": "QICE_MELT",
        "units": "mm/s",
        "description": "ice melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "QICE": {
        "standard_name": "specific_humidity",
        "cesm_name": "QICE",
        "units": "mm/s",
        "description": "ice growth/melt",
        "domain": "atmosphere",
        "component": "std"
    },
    "QINFL": {
        "standard_name": "specific_humidity",
        "cesm_name": "QINFL",
        "units": "mm/s",
        "description": "infiltration",
        "domain": "atmosphere",
        "component": "std"
    },
    "QIRRIG": {
        "standard_name": "specific_humidity",
        "cesm_name": "QIRRIG",
        "units": "mm/s",
        "description": "water added through irrigation",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRGWL": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRGWL",
        "units": "mm/s",
        "description": "surface runoff at glaciers (liquid only) wetlands lakes; also includes melted ice runoff from QSNWCPICE",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRUNOFF_ICE": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRUNOFF_ICE",
        "units": "mm/s",
        "description": "total liquid runoff not incl corret for LULCC (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRUNOFF_ICE_TO_COUPLER": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRUNOFF_ICE_TO_COUPLER",
        "units": "mm/s",
        "description": "total ice runoff sent to coupler (includes corrections for land use change)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QRUNOFF_TO_COUPLER": {
        "standard_name": "specific_humidity",
        "cesm_name": "QRUNOFF_TO_COUPLER",
        "units": "mm/s",
        "description": "total liquid runoff sent to coupler (includes corrections for land use change)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNOCPLIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSNOCPLIQ",
        "units": "mm H2O/s",
        "description": "excess liquid h2o due to snow capping not including correction for land use change",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNOFRZ_ICE": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSNOFRZ_ICE",
        "units": "mm/s",
        "description": "column-integrated snow freezing rate (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNOMELT_ICE": {
        "standard_name": "air_temperature",
        "cesm_name": "QSNOMELT_ICE",
        "units": "mm/s",
        "description": "snow melt (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNOMELT": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSNOMELT",
        "units": "mm/s",
        "description": "snow melt rate",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNO_TEMPUNLOAD": {
        "standard_name": "air_temperature",
        "cesm_name": "QSNO_TEMPUNLOAD",
        "units": "mm/s",
        "description": "canopy snow temp unloading",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNO_WINDUNLOAD": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSNO_WINDUNLOAD",
        "units": "mm/s",
        "description": "canopy snow wind unloading",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSNWCPICE": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSNWCPICE",
        "units": "mm H2O/s",
        "description": "excess solid h2o due to snow capping not including correction for land use change",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSOIL_ICE": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSOIL_ICE",
        "units": "mm/s",
        "description": "Ground evaporation (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "RAIN_FROM_ATM": {
        "standard_name": "precipitation_flux",
        "cesm_name": "RAIN_FROM_ATM",
        "units": "mm/s",
        "description": "atmospheric rain received from atmosphere (pre-repartitioning)",
        "domain": "atmosphere",
        "component": "std"
    },
    "RAIN_ICE": {
        "standard_name": "precipitation_flux",
        "cesm_name": "RAIN_ICE",
        "units": "mm/s",
        "description": "atmospheric rain after rain/snow repartitioning based on temperature (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "RC13_CANAIR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RC13_CANAIR",
        "units": "proportion",
        "description": "C13/C(12+13) for canopy air",
        "domain": "atmosphere",
        "component": "std"
    },
    "RC13_PSNSHA": {
        "standard_name": "air_pressure",
        "cesm_name": "RC13_PSNSHA",
        "units": "proportion",
        "description": "C13/C(12+13) for shaded photosynthesis",
        "domain": "atmosphere",
        "component": "std"
    },
    "RC13_PSNSUN": {
        "standard_name": "air_pressure",
        "cesm_name": "RC13_PSNSUN",
        "units": "proportion",
        "description": "C13/C(12+13) for sunlit photosynthesis",
        "domain": "atmosphere",
        "component": "std"
    },
    "RSSHA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RSSHA",
        "units": "s/m",
        "description": "shaded leaf stomatal resistance",
        "domain": "atmosphere",
        "component": "std"
    },
    "RSSUN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RSSUN",
        "units": "s/m",
        "description": "sunlit leaf stomatal resistance",
        "domain": "atmosphere",
        "component": "std"
    },
    "SABG_PEN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SABG_PEN",
        "units": "watt/m^2",
        "description": "Rural solar rad penetrating top soil or snow layer",
        "domain": "atmosphere",
        "component": "std"
    },
    "SLASH_HARVESTC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SLASH_HARVESTC",
        "units": "gC/m^2/s",
        "description": "slash harvest carbon (to litter)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SMIN_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SMIN_NH4",
        "units": "gN/m^2",
        "description": "soil mineral NH4",
        "domain": "atmosphere",
        "component": "std"
    },
    "SMIN_NO3_LEACHED": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SMIN_NO3_LEACHED",
        "units": "gN/m^2/s",
        "description": "soil NO3 pool loss to leaching",
        "domain": "atmosphere",
        "component": "std"
    },
    "SMIN_NO3_RUNOFF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SMIN_NO3_RUNOFF",
        "units": "gN/m^2/s",
        "description": "soil NO3 pool loss to runoff",
        "domain": "atmosphere",
        "component": "std"
    },
    "SMIN_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SMIN_NO3",
        "units": "gN/m^2",
        "description": "soil mineral NO3",
        "domain": "atmosphere",
        "component": "std"
    },
    "SMINN_TO_PLANT_FUN": {
        "standard_name": "air_temperature",
        "cesm_name": "SMINN_TO_PLANT_FUN",
        "units": "gN/m^2/s",
        "description": "Total soil N uptake of FUN",
        "domain": "atmosphere",
        "component": "std"
    },
    "SMP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SMP",
        "units": "mm",
        "description": "soil matric potential (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOINTABS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOINTABS",
        "units": "no units",
        "description": "Fraction of incoming solar absorbed by lower snow layers",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOTXMASS_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOTXMASS_ICE",
        "units": "K kg/m2",
        "description": "snow temperature times layer mass layer sum (ice landunits only); to get mass-weighted temperature divide by (SNOWICE_ICE+SNOWLIQ_ICE)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOUNLOAD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SNOUNLOAD",
        "units": "mm",
        "description": "Canopy snow unloading",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOW_DEPTH": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOW_DEPTH",
        "units": "m",
        "description": "snow height of snow covered area",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOW_FROM_ATM": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOW_FROM_ATM",
        "units": "mm/s",
        "description": "atmospheric snow received from atmosphere (pre-repartitioning)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOWICE_ICE": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOWICE_ICE",
        "units": "kg/m2",
        "description": "snow ice (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOW_ICE": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOW_ICE",
        "units": "mm/s",
        "description": "atmospheric snow after rain/snow repartitioning based on temperature (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOWLIQ_ICE": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOWLIQ_ICE",
        "units": "kg/m2",
        "description": "snow liquid water (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOW_PERSISTENCE": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOW_PERSISTENCE",
        "units": "seconds",
        "description": "Length of time of continuous snow cover (nat. veg. landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SNOW_SOURCES": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOW_SOURCES",
        "units": "mm/s",
        "description": "snow sources (liquid water)",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOILC_CHANGE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOILC_CHANGE",
        "units": "gC/m^2/s",
        "description": "C change in soil",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOILC_HR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOILC_HR",
        "units": "gC/m^2/s",
        "description": "soil C heterotrophic respiration",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOILRESIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOILRESIS",
        "units": "s/m",
        "description": "soil resistance to evaporation",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOMC_FIRE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOMC_FIRE",
        "units": "gC/m^2/s",
        "description": "C loss due to peat burning",
        "domain": "atmosphere",
        "component": "std"
    },
    "SOM_C_LEACHED": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SOM_C_LEACHED",
        "units": "gC/m^2/s",
        "description": "total flux of C from SOM pools due to leaching",
        "domain": "atmosphere",
        "component": "std"
    },
    "SWBGT_R": {
        "standard_name": "air_temperature",
        "cesm_name": "SWBGT_R",
        "units": "C",
        "description": "Rural 2 m Simplified Wetbulb Globe Temp",
        "domain": "atmosphere",
        "component": "std"
    },
    "SWBGT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SWBGT",
        "units": "C",
        "description": "2 m Simplified Wetbulb Globe Temp",
        "domain": "atmosphere",
        "component": "std"
    },
    "SWBGT_U": {
        "standard_name": "air_temperature",
        "cesm_name": "SWBGT_U",
        "units": "C",
        "description": "Urban 2 m Simplified Wetbulb Globe Temp",
        "domain": "atmosphere",
        "component": "std"
    },
    "TBOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TBOT",
        "units": "K",
        "description": "atmospheric air temperature (downscaled to columns in glacier regions)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TG_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TG_ICE",
        "units": "K",
        "description": "ground temperature (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TH2OSFC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TH2OSFC",
        "units": "K",
        "description": "surface water temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TKE1": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TKE1",
        "units": "W/(mK)",
        "description": "top lake level eddy thermal conductivity",
        "domain": "atmosphere",
        "component": "std"
    },
    "TLAKE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TLAKE",
        "units": "K",
        "description": "lake temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOPO_COL_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOPO_COL_ICE",
        "units": "m",
        "description": "column-level topographic height (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTCOLCH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTCOLCH4",
        "units": "gC/m2",
        "description": "total belowground CH4 (0 for non-lake special landunits in the absence of dynamic landunits)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTECOSYSN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTECOSYSN",
        "units": "gN/m^2",
        "description": "total ecosystem N excluding product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTLITC_1m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTLITC_1m",
        "units": "gC/m^2",
        "description": "total litter carbon to 1 meter depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTLITN_1m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTLITN_1m",
        "units": "gN/m^2",
        "description": "total litter N to 1 meter",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTSOMN_1m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTSOMN_1m",
        "units": "gN/m^2",
        "description": "total soil organic matter N to 1 meter",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTVEGN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTVEGN",
        "units": "gN/m^2",
        "description": "total vegetation nitrogen",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOT_WOODPRODC_LOSS": {
        "standard_name": "air_temperature",
        "cesm_name": "TOT_WOODPRODC_LOSS",
        "units": "gC/m^2/s",
        "description": "total loss from wood product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOT_WOODPRODN_LOSS": {
        "standard_name": "air_temperature",
        "cesm_name": "TOT_WOODPRODN_LOSS",
        "units": "gN/m^2/s",
        "description": "total loss from wood product pools",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOT_WOODPRODN": {
        "standard_name": "air_temperature",
        "cesm_name": "TOT_WOODPRODN",
        "units": "gN/m^2",
        "description": "total wood product N",
        "domain": "atmosphere",
        "component": "std"
    },
    "TPU25T": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TPU25T",
        "units": "umol/m2/s",
        "description": "canopy profile of tpu",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSA_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSA_ICE",
        "units": "K",
        "description": "2m air temperature (ice landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "T_SCALAR": {
        "standard_name": "air_temperature",
        "cesm_name": "T_SCALAR",
        "units": "unitless",
        "description": "temperature inhibition of decomposition",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSL",
        "units": "K",
        "description": "temperature of near-surface soil layer (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TSOI_10CM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TSOI_10CM",
        "units": "K",
        "description": "soil temperature in top 10cm of soil",
        "domain": "atmosphere",
        "component": "std"
    },
    "U10_DUST": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "U10_DUST",
        "units": "m/s",
        "description": "10-m wind for dust model",
        "domain": "atmosphere",
        "component": "std"
    },
    "VCMX25T": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VCMX25T",
        "units": "umol/m2/s",
        "description": "canopy profile of vcmax25",
        "domain": "atmosphere",
        "component": "std"
    },
    "Vcmx25Z": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Vcmx25Z",
        "units": "umol/m2/s",
        "description": "canopy profile of vcmax25 predicted by LUNA model",
        "domain": "atmosphere",
        "component": "std"
    },
    "VEGWP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VEGWP",
        "units": "mm",
        "description": "vegetation water matric potential for sun/sha canopy xyl root segments",
        "domain": "atmosphere",
        "component": "std"
    },
    "VOLRMCH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VOLRMCH",
        "units": "m3",
        "description": "river channel main channel water storage",
        "domain": "atmosphere",
        "component": "std"
    },
    "VOLR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VOLR",
        "units": "m3",
        "description": "river channel total water storage",
        "domain": "atmosphere",
        "component": "std"
    },
    "WA": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WA",
        "units": "mm",
        "description": "water in the unconfined aquifer (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "WBT_R": {
        "standard_name": "air_temperature",
        "cesm_name": "WBT_R",
        "units": "C",
        "description": "Rural 2 m Stull Wet Bulb",
        "domain": "atmosphere",
        "component": "std"
    },
    "WBT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WBT",
        "units": "C",
        "description": "2 m Stull Wet Bulb",
        "domain": "atmosphere",
        "component": "std"
    },
    "WBT_U": {
        "standard_name": "air_temperature",
        "cesm_name": "WBT_U",
        "units": "C",
        "description": "Urban 2 m Stull Wet Bulb",
        "domain": "atmosphere",
        "component": "std"
    },
    "WIND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WIND",
        "units": "m/s",
        "description": "atmospheric wind velocity magnitude",
        "domain": "atmosphere",
        "component": "std"
    },
    "W_SCALAR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "W_SCALAR",
        "units": "unitless",
        "description": "Moisture (dryness) inhibition of decomposition",
        "domain": "atmosphere",
        "component": "std"
    },
    "WTGQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "WTGQ",
        "units": "m/s",
        "description": "surface tracer conductance",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZWT_CH4_UNSAT": {
        "standard_name": "air_temperature",
        "cesm_name": "ZWT_CH4_UNSAT",
        "units": "m",
        "description": "depth of water table for methane production used in non-inundated area",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZWT_PERCH": {
        "standard_name": "air_temperature",
        "cesm_name": "ZWT_PERCH",
        "units": "m",
        "description": "perched water table depth (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "ZWT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ZWT",
        "units": "m",
        "description": "water table depth (vegetated landunits only)",
        "domain": "atmosphere",
        "component": "std"
    },
    "diazC_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diazC_zint_100m",
        "units": "mmol/m^3 cm",
        "description": "Diazotroph Carbon 0-100m Vertical Integral",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DpCO2_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DpCO2_2",
        "units": "ppmv",
        "description": "D pCO2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ECOSYS_XKW_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ECOSYS_XKW_2",
        "units": "cm/s",
        "description": "XKW for ecosys fluxes",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FG_CO2_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FG_CO2_2",
        "units": "mmol/m^3 cm/s",
        "description": "DIC Surface Gas Flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "spCaCO3_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "spCaCO3_zint_100m",
        "units": "mmol/m^3 cm",
        "description": "Small Phyto CaCO3 0-100m Vertical Integral",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SST2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SST2",
        "units": "degC^2",
        "description": "Surface Potential Temperature**2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "STF_O2_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STF_O2_2",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Oxygen Surface Flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "XBLT_2": {
        "standard_name": "air_temperature",
        "cesm_name": "XBLT_2",
        "units": "centimeter",
        "description": "Maximum Boundary-Layer Depth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "XMXL_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "XMXL_2",
        "units": "centimeter",
        "description": "Maximum Mixed-Layer Depth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CFC_ATM_PRESS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CFC_ATM_PRESS",
        "units": "atmospheres",
        "description": "Atmospheric Pressure for CFC fluxes",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CFC_IFRAC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CFC_IFRAC",
        "units": "fraction",
        "description": "Ice Fraction for CFC fluxes",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CFC_XKW": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CFC_XKW",
        "units": "cm/s",
        "description": "XKW for CFC fluxes",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DCO2STAR_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "DCO2STAR_ALT_CO2",
        "units": "mmol/m^3",
        "description": "D CO2 Star Alternative CO2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DCO2STAR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DCO2STAR",
        "units": "mmol/m^3",
        "description": "D CO2 Star",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DIA_DEPTH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIA_DEPTH",
        "units": "cm",
        "description": "Depth of the Diabatic Region at the Surface",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DON_prod": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DON_prod",
        "units": "mmol/m^3/s",
        "description": "DON Production",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DOP_prod": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOP_prod",
        "units": "mmol/m^3/s",
        "description": "DOP Production",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dTEMP_NEG_2D": {
        "standard_name": "air_temperature",
        "cesm_name": "dTEMP_NEG_2D",
        "units": "degC",
        "description": "min neg column temperature timestep diff",
        "domain": "atmosphere",
        "component": "moar"
    },
    "dTEMP_POS_2D": {
        "standard_name": "air_temperature",
        "cesm_name": "dTEMP_POS_2D",
        "units": "degC",
        "description": "max pos column temperature timestep diff",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ECOSYS_ATM_PRESS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ECOSYS_ATM_PRESS",
        "units": "atmospheres",
        "description": "Atmospheric Pressure for ecosys fluxes",
        "domain": "atmosphere",
        "component": "moar"
    },
    "ECOSYS_XKW": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ECOSYS_XKW",
        "units": "cm/s",
        "description": "XKW for ecosys fluxes",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Fe_scavenge_rate": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Fe_scavenge_rate",
        "units": "1/y",
        "description": "Iron Scavenging Rate",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Fe_scavenge": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Fe_scavenge",
        "units": "mmol/m^3/s",
        "description": "Iron Scavenging",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FvICE_ALK": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FvICE_ALK",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Virtual Surface Flux ICE",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FvICE_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FvICE_DIC",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Virtual Surface Flux ICE",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FvPER_ALK": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FvPER_ALK",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Virtual Surface Flux PER",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FvPER_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FvPER_DIC",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Virtual Surface Flux PER",
        "domain": "atmosphere",
        "component": "moar"
    },
    "FW": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FW",
        "units": "centimeter/s",
        "description": "Freshwater Flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "H2CO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "H2CO3",
        "units": "mmol/m^3",
        "description": "Carbonic Acid Concentration",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HBLT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HBLT",
        "units": "centimeter",
        "description": "Boundary-Layer Depth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFS",
        "units": "centimeter gram/kilogram/s",
        "description": "Vertically Integrated Horz Diff S tendency",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HLS_SUBM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HLS_SUBM",
        "units": "cm",
        "description": "Horizontal length scale used in submeso",
        "domain": "atmosphere",
        "component": "moar"
    },
    "INT_DEPTH": {
        "standard_name": "air_temperature",
        "cesm_name": "INT_DEPTH",
        "units": "cm",
        "description": "Depth at which the Interior Region Starts",
        "domain": "atmosphere",
        "component": "moar"
    },
    "IRON_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "IRON_FLUX",
        "units": "mmol/m^2/s",
        "description": "Atmospheric Iron Flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_ALK": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_ALK",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_DIC": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_DIC",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_DOC": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_DOC",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Organic Carbon Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_Fe": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_Fe",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Iron Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_NH4": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_NH4",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Ammonia Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_NO3": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_NO3",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Nitrate Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_O2": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_O2",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Oxygen Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_PO4": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_PO4",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Phosphate Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "Jint_100m_SiO3": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_SiO3",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Silicate Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "KVMIX_M": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "KVMIX_M",
        "units": "centimeter^2/s",
        "description": "Vertical viscosity due to Tidal Mixing+background",
        "domain": "atmosphere",
        "component": "moar"
    },
    "MELT_F": {
        "standard_name": "air_temperature",
        "cesm_name": "MELT_F",
        "units": "kg/m^2/s",
        "description": "Melt Flux from Coupler",
        "domain": "atmosphere",
        "component": "moar"
    },
    "MELTH_F": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MELTH_F",
        "units": "watt/m^2",
        "description": "Melt Heat Flux from Coupler",
        "domain": "atmosphere",
        "component": "moar"
    },
    "NHy_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NHy_FLUX",
        "units": "nmol/cm^2/s",
        "description": "Flux of NHy from Atmosphere",
        "domain": "atmosphere",
        "component": "moar"
    },
    "N_SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "N_SALT",
        "units": "gram centimeter^3/kg/s",
        "description": "Northward Salt Transport",
        "domain": "atmosphere",
        "component": "moar"
    },
    "O2_CONSUMPTION": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "O2_CONSUMPTION",
        "units": "mmol/m^3/s",
        "description": "O2 Consumption",
        "domain": "atmosphere",
        "component": "moar"
    },
    "O2_PRODUCTION": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "O2_PRODUCTION",
        "units": "mmol/m^3/s",
        "description": "O2 Production",
        "domain": "atmosphere",
        "component": "moar"
    },
    "O2SAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "O2SAT",
        "units": "mmol/m^3",
        "description": "O2 Saturation",
        "domain": "atmosphere",
        "component": "moar"
    },
    "PH_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "PH_ALT_CO2",
        "units": "1",
        "description": "Surface pH Alternative CO2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "P_iron_FLUX_IN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "P_iron_FLUX_IN",
        "units": "mmol/m^3 cm/s",
        "description": "P_iron Flux into Cell",
        "domain": "atmosphere",
        "component": "moar"
    },
    "P_iron_PROD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "P_iron_PROD",
        "units": "mmol/m^3/s",
        "description": "P_iron Production",
        "domain": "atmosphere",
        "component": "moar"
    },
    "QSW_HBL": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_HBL",
        "units": "watt/m^2",
        "description": "Solar Short-Wave Heat Flux in bndry layer",
        "domain": "atmosphere",
        "component": "moar"
    },
    "QSW_HTP": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_HTP",
        "units": "watt/m^2",
        "description": "Solar Short-Wave Heat Flux in top layer",
        "domain": "atmosphere",
        "component": "moar"
    },
    "RESID_S": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RESID_S",
        "units": "kg/m^2/s",
        "description": "Free-Surface Residual Flux (S)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SALT_F": {
        "standard_name": "air_temperature",
        "cesm_name": "SALT_F",
        "units": "kg/m^2/s",
        "description": "Salt Flux from Coupler (kg of salt/m^2/s)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SCHMIDT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "SCHMIDT_CO2",
        "units": "1",
        "description": "CO2 Schmidt Number",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SCHMIDT_O2": {
        "standard_name": "air_temperature",
        "cesm_name": "SCHMIDT_O2",
        "units": "1",
        "description": "O2 Schmidt Number",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SENH_F": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SENH_F",
        "units": "watt/m^2",
        "description": "Sensible Heat Flux from Coupler",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SFWF_WRST": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFWF_WRST",
        "units": "kg/m^2/s",
        "description": "Virtual Salt Flux due to weak restoring",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SiO2_FLUX_IN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SiO2_FLUX_IN",
        "units": "mmol/m^3 cm/s",
        "description": "SiO2 Flux into Cell",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SNOW_F": {
        "standard_name": "snowfall_flux",
        "cesm_name": "SNOW_F",
        "units": "kg/m^2/s",
        "description": "Snow Flux from Coupler",
        "domain": "atmosphere",
        "component": "moar"
    },
    "SSH2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SSH2",
        "units": "cm^2",
        "description": "SSH**2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "STF_CFC11": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STF_CFC11",
        "units": "fmol/cm^2/s",
        "description": "CFC11 Surface Flux excludes FvICE term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "STF_CFC12": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STF_CFC12",
        "units": "fmol/cm^2/s",
        "description": "CFC12 Surface Flux excludes FvICE term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "STF_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STF_O2",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Oxygen Surface Flux excludes FvICE term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TBLT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TBLT",
        "units": "centimeter",
        "description": "Minimum Boundary-Layer Depth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_ALK": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_ALK",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_DIC_ALT_CO2",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Alternative CO2 Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_DIC": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_DIC",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_DOC": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_DOC",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Organic Carbon Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_Fe": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_Fe",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Iron Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_NH4": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_NH4",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Ammonia Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_NO3": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_NO3",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Nitrate Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_O2": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_O2",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Oxygen Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "tend_zint_100m_PO4": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_PO4",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Phosphate Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TFW_S": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TFW_S",
        "units": "kg/m^2/s",
        "description": "S flux due to freshwater flux (kg of salt/m^2/s)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TFW_T": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TFW_T",
        "units": "watt/m^2",
        "description": "T flux due to freshwater flux",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TLT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TLT",
        "units": "cm",
        "description": "Transition Layer Thickness",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TMXL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMXL",
        "units": "centimeter",
        "description": "Minimum Mixed-Layer Depth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "TPOWER": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TPOWER",
        "units": "erg/s/cm^3",
        "description": "Energy Used by Vertical Mixing",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VDC_S": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VDC_S",
        "units": "cm^2/s",
        "description": "total diabatic vertical SALT diffusivity",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VNS_ISOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VNS_ISOP",
        "units": "gram/kilogram/s",
        "description": "Salt Flux Tendency in grid-y Dir due to Eddy-Induced Vel (diagnostic)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VNS_SUBM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VNS_SUBM",
        "units": "gram/kilogram/s",
        "description": "Salt Flux Tendency in grid-y Dir due to submeso Vel (diagnostic)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VNT_SUBM": {
        "standard_name": "air_temperature",
        "cesm_name": "VNT_SUBM",
        "units": "degC/s",
        "description": "Heat Flux Tendency in grid-y Dir due to submeso Vel (diagnostic)",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VVC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VVC",
        "units": "cm^2/s",
        "description": "total vertical momentum viscosity",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WVEL2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WVEL2",
        "units": "centimeter^2/s^2",
        "description": "Vertical Velocity**2",
        "domain": "atmosphere",
        "component": "moar"
    },
    "XBLT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "XBLT",
        "units": "centimeter",
        "description": "Maximum Boundary-Layer Depth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "zsatarag": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "zsatarag",
        "units": "cm",
        "description": "Aragonite Saturation Depth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "zsatcalc": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "zsatcalc",
        "units": "cm",
        "description": "Calcite Saturation Depth",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DIA_IMPVF_DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIA_IMPVF_DOC",
        "units": "mmol/m^3 cm/s",
        "description": "DOC Flux Across Bottom Face from Diabatic Implicit Vertical Mixing",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DIA_IMPVF_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIA_IMPVF_Fe",
        "units": "mmol/m^3 cm/s",
        "description": "Fe Flux Across Bottom Face from Diabatic Implicit Vertical Mixing",
        "domain": "atmosphere",
        "component": "moar"
    },
    "DIA_IMPVF_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIA_IMPVF_O2",
        "units": "mmol/m^3 cm/s",
        "description": "O2 Flux Across Bottom Face from Diabatic Implicit Vertical Mixing",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFB_DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFB_DOC",
        "units": "mmol/m^3/s",
        "description": "DOC Horizontal Diffusive Flux across Bottom Face",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFB_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFB_Fe",
        "units": "mmol/m^3/s",
        "description": "Fe Horizontal Diffusive Flux across Bottom Face",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFB_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFB_O2",
        "units": "mmol/m^3/s",
        "description": "O2 Horizontal Diffusive Flux across Bottom Face",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFE_DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFE_DOC",
        "units": "mmol/m^3/s",
        "description": "DOC Horizontal Diffusive Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFE_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFE_Fe",
        "units": "mmol/m^3/s",
        "description": "Fe Horizontal Diffusive Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFE_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFE_O2",
        "units": "mmol/m^3/s",
        "description": "O2 Horizontal Diffusive Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFN_DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFN_DOC",
        "units": "mmol/m^3/s",
        "description": "DOC Horizontal Diffusive Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFN_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFN_Fe",
        "units": "mmol/m^3/s",
        "description": "Fe Horizontal Diffusive Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "HDIFN_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFN_O2",
        "units": "mmol/m^3/s",
        "description": "O2 Horizontal Diffusive Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "J_ALK": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "J_ALK",
        "units": "meq/m^3/s",
        "description": "Alkalinity Source Sink Term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "J_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "J_Fe",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Iron Source Sink Term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "J_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "J_NH4",
        "units": "mmol/m^3/s",
        "description": "Dissolved Ammonia Source Sink Term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "J_PO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "J_PO4",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Phosphate Source Sink Term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "KPP_SRC_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "KPP_SRC_Fe",
        "units": "mmol/m^3/s",
        "description": "Fe tendency from KPP non local mixing term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "KPP_SRC_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "KPP_SRC_O2",
        "units": "mmol/m^3/s",
        "description": "O2 tendency from KPP non local mixing term",
        "domain": "atmosphere",
        "component": "moar"
    },
    "UE_DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UE_DOC",
        "units": "mmol/m^3/s",
        "description": "DOC Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "UE_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UE_Fe",
        "units": "mmol/m^3/s",
        "description": "Fe Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "UE_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UE_O2",
        "units": "mmol/m^3/s",
        "description": "O2 Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VN_DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VN_DOC",
        "units": "mmol/m^3/s",
        "description": "DOC Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VN_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VN_Fe",
        "units": "mmol/m^3/s",
        "description": "Fe Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "VN_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VN_O2",
        "units": "mmol/m^3/s",
        "description": "O2 Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WT_DOC": {
        "standard_name": "air_temperature",
        "cesm_name": "WT_DOC",
        "units": "mmol/m^3/s",
        "description": "DOC Flux Across Top Face",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WT_Fe": {
        "standard_name": "air_temperature",
        "cesm_name": "WT_Fe",
        "units": "mmol/m^3/s",
        "description": "Fe Flux Across Top Face",
        "domain": "atmosphere",
        "component": "moar"
    },
    "WT_O2": {
        "standard_name": "air_temperature",
        "cesm_name": "WT_O2",
        "units": "mmol/m^3/s",
        "description": "O2 Flux Across Top Face",
        "domain": "atmosphere",
        "component": "moar"
    },
    "CaCO3_form_zint_2": {
        "standard_name": "air_temperature",
        "cesm_name": "CaCO3_form_zint_2",
        "units": "mmol/m^3 cm/s",
        "description": "Total CaCO3 Formation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diatChl_SURF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diatChl_SURF",
        "units": "mg/m^3",
        "description": "Diatom Chlorophyll Surface Value",
        "domain": "atmosphere",
        "component": "std"
    },
    "diatC_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diatC_zint_100m",
        "units": "mmol/m^3 cm",
        "description": "Diatom Carbon 0-100m Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diazChl_SURF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diazChl_SURF",
        "units": "mg/m^3",
        "description": "Diazotroph Chlorophyll Surface Value",
        "domain": "atmosphere",
        "component": "std"
    },
    "ECOSYS_IFRAC_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ECOSYS_IFRAC_2",
        "units": "fraction",
        "description": "Ice Fraction for ecosys fluxes",
        "domain": "atmosphere",
        "component": "std"
    },
    "HBLT_2": {
        "standard_name": "air_temperature",
        "cesm_name": "HBLT_2",
        "units": "centimeter",
        "description": "Boundary-Layer Depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "HMXL_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HMXL_2",
        "units": "centimeter",
        "description": "Mixed-Layer Depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "HMXL_DR_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HMXL_DR_2",
        "units": "centimeter",
        "description": "Mixed-Layer Depth (density)",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_diat_zint_2": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_diat_zint_2",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom C Fixation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_diaz_zint_2": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_diaz_zint_2",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph C Fixation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_sp_zint_2": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_sp_zint_2",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto C Fixation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "spChl_SURF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "spChl_SURF",
        "units": "mg/m^3",
        "description": "Small Phyto Chlorophyll Surface Value",
        "domain": "atmosphere",
        "component": "std"
    },
    "spC_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "spC_zint_100m",
        "units": "mmol/m^3 cm",
        "description": "Small Phyto Carbon 0-100m Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "SSH2_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SSH2_2",
        "units": "cm^2",
        "description": "SSH**2",
        "domain": "atmosphere",
        "component": "std"
    },
    "SSH_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SSH_2",
        "units": "centimeter",
        "description": "Sea Surface Height",
        "domain": "atmosphere",
        "component": "std"
    },
    "SSS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SSS",
        "units": "(gram/kilogram)",
        "description": "Sea Surface Salinity",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUX_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUX_2",
        "units": "dyne/centimeter^2",
        "description": "Windstress in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUY_2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUY_2",
        "units": "dyne/centimeter^2",
        "description": "Windstress in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "WVEL_50m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WVEL_50m",
        "units": "centimeter/s",
        "description": "Vertical Velocity at 50m Depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "zooC_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "zooC_zint_100m",
        "units": "mmol/m^3 cm",
        "description": "Zooplankton Carbon 0-100m Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "co3_sat_arag": {
        "standard_name": "air_temperature",
        "cesm_name": "co3_sat_arag",
        "units": "mmol/m^3",
        "description": "CO3 concentration at aragonite saturation",
        "domain": "atmosphere",
        "component": "std"
    },
    "co3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "co3",
        "units": "mmol/m^3",
        "description": "CO3 concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "diacZ": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diacZ",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_agg": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_agg",
        "units": "mmol/m^3/s",
        "description": "Diatom Aggregation",
        "domain": "atmosphere",
        "component": "std"
    },
    "diatChl": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diatChl",
        "units": "mg/m^3",
        "description": "Diatom Chlorophyll",
        "domain": "atmosphere",
        "component": "std"
    },
    "diatC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diatC",
        "units": "mmol/m^3",
        "description": "Diatom Carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_Fe_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_Fe_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Diatom Fe Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_light_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_light_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Diatom Light Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_loss": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_loss",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_N_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_N_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Diatom N Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_P_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_P_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Diatom P Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_SiO3_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_SiO3_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Diatom SiO3 Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_agg": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_agg",
        "units": "mmol/m^3/s",
        "description": "Diazotroph Aggregation",
        "domain": "atmosphere",
        "component": "std"
    },
    "diazChl": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diazChl",
        "units": "mg/m^3",
        "description": "Diazotroph Chlorophyll",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_Fe_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diaz_Fe_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Diazotroph Fe Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_light_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diaz_light_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Diazotroph Light Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_loss": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_loss",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_P_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diaz_P_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Diazotroph P Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "DpCO2_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "DpCO2_ALT_CO2",
        "units": "ppmv",
        "description": "D pCO2 Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "DpCO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DpCO2",
        "units": "ppmv",
        "description": "D pCO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "FG_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "FG_ALT_CO2",
        "units": "mmol/m^3 cm/s",
        "description": "DIC Surface Gas Flux Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "FG_CO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FG_CO2",
        "units": "mmol/m^3 cm/s",
        "description": "DIC Surface Gas Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_diat",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_diaz",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_sp",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "O2",
        "units": "mmol/m^3",
        "description": "Dissolved Oxygen",
        "domain": "atmosphere",
        "component": "std"
    },
    "PAR_avg": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PAR_avg",
        "units": "W/m^2",
        "description": "PAR Average over Model Cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "pCO2SURF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pCO2SURF",
        "units": "ppmv",
        "description": "surface pCO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "PD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PD",
        "units": "gram/centimeter^3",
        "description": "Potential Density Ref to Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "pH_3D": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pH_3D",
        "units": "1",
        "description": "pH",
        "domain": "atmosphere",
        "component": "std"
    },
    "PhotoC_diat": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PhotoC_diat",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "PhotoC_diaz": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PhotoC_diaz",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "PhotoC_sp": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PhotoC_sp",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "PO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PO4",
        "units": "mmol/m^3",
        "description": "Dissolved Inorganic Phosphate",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_FLUX_100": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_FLUX_100",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SALT",
        "units": "gram/kilogram",
        "description": "Salinity",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_agg": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_agg",
        "units": "mmol/m^3/s",
        "description": "Small Phyto Aggregation",
        "domain": "atmosphere",
        "component": "std"
    },
    "spChl": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "spChl",
        "units": "mg/m^3",
        "description": "Small Phyto Chlorophyll",
        "domain": "atmosphere",
        "component": "std"
    },
    "spC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "spC",
        "units": "mmol/m^3",
        "description": "Small Phyto Carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_Fe_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "sp_Fe_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Small Phyto Fe Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_light_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "sp_light_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Small Phyto Light Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_loss": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_loss",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_N_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "sp_N_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Small Phyto N Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_P_lim_Cweight_avg_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "sp_P_lim_Cweight_avg_100m",
        "units": "1",
        "description": "Small Phyto P Limitation carbon biomass weighted average over 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEMP": {
        "standard_name": "air_temperature",
        "cesm_name": "TEMP",
        "units": "degC",
        "description": "Potential Temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "UISOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UISOP",
        "units": "cm/s",
        "description": "Bolus Velocity in grid-x direction (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "USUBM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "USUBM",
        "units": "cm/s",
        "description": "Submeso velocity in grid-x direction (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "UVEL": {
        "standard_name": "eastward_wind",
        "cesm_name": "UVEL",
        "units": "centimeter/s",
        "description": "Velocity in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VISOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VISOP",
        "units": "cm/s",
        "description": "Bolus Velocity in grid-y direction (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "VSUBM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VSUBM",
        "units": "cm/s",
        "description": "Submeso velocity in grid-y direction (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "VVEL": {
        "standard_name": "northward_wind",
        "cesm_name": "VVEL",
        "units": "centimeter/s",
        "description": "Velocity in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "WVEL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WVEL",
        "units": "centimeter/s",
        "description": "Vertical Velocity",
        "domain": "atmosphere",
        "component": "std"
    },
    "zooC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "zooC",
        "units": "mmol/m^3",
        "description": "Zooplankton Carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_ALK_SURF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_ALK_SURF",
        "units": "neq/cm3",
        "description": "Abiotic Surface Alkalinity",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_CO2STAR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_CO2STAR",
        "units": "nmol/cm^3",
        "description": "ABIO_CO2STAR",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_D14Catm": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_D14Catm",
        "units": "permil",
        "description": "Abiotic atmospheric Delta C14 in permil",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_D14Cocn": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_D14Cocn",
        "units": "permil",
        "description": "Abiotic oceanic Delta C14 in permil",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_DCO2STAR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_DCO2STAR",
        "units": "nmol/cm^3",
        "description": "ABIO_DCO2STAR",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_DIC14": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_DIC14",
        "units": "nmol/cm^3",
        "description": "ABIO_DIC14",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_DIC",
        "units": "nmol/cm^3",
        "description": "ABIO_DIC",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_DpCO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_DpCO2",
        "units": "ppmv",
        "description": "ABIO_DpCO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_pCO2SURF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_pCO2SURF",
        "units": "ppmv",
        "description": "ABIO_pCO2SURF",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_pCO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_pCO2",
        "units": "ppm",
        "description": "Abiotic CO2 atmospheric partial pressure",
        "domain": "atmosphere",
        "component": "std"
    },
    "ABIO_PH_SURF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ABIO_PH_SURF",
        "units": "none",
        "description": "Abiotic Surface PH",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADV_3D_SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ADV_3D_SALT",
        "units": "gram/kilogram/s",
        "description": "SALT Advection Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADV_3D_TEMP": {
        "standard_name": "air_temperature",
        "cesm_name": "ADV_3D_TEMP",
        "units": "degC/s",
        "description": "TEMP Advection Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADVS_ISOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ADVS_ISOP",
        "units": "cm gram/kilogram/s",
        "description": "Vertically-Integrated S Eddy-Induced Advection Tendency (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADVS_SUBM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ADVS_SUBM",
        "units": "cm gram/kilogram/s",
        "description": "Vertically-Integrated S submeso Advection Tendency (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADVS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ADVS",
        "units": "centimeter gram/kilogram/s",
        "description": "Vertically-Integrated S Advection Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADVT_ISOP": {
        "standard_name": "air_temperature",
        "cesm_name": "ADVT_ISOP",
        "units": "cm degC/s",
        "description": "Vertically-Integrated T Eddy-Induced Advection Tendency (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADVT_SUBM": {
        "standard_name": "air_temperature",
        "cesm_name": "ADVT_SUBM",
        "units": "cm degC/s",
        "description": "Vertically-Integrated T submeso Advection Tendency (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADVT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ADVT",
        "units": "centimeter degC/s",
        "description": "Vertically-Integrated T Advection Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADVU": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ADVU",
        "units": "centimeter/s^2",
        "description": "Advection in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "ADVV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ADVV",
        "units": "centimeter/s^2",
        "description": "Advection in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "ALK_ALT_CO2_RESTORE_TEND": {
        "standard_name": "air_temperature",
        "cesm_name": "ALK_ALT_CO2_RESTORE_TEND",
        "units": "meq/m^3/s",
        "description": "Alkalinity Alternative CO2 Restoring Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "ALK_ALT_CO2_RIV_FLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "ALK_ALT_CO2_RIV_FLUX",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Alternative CO2 Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "ALK_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "ALK_ALT_CO2",
        "units": "meq/m^3",
        "description": "Alkalinity Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "ALK_RESTORE_TEND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ALK_RESTORE_TEND",
        "units": "meq/m^3/s",
        "description": "Alkalinity Restoring Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "ALK_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ALK_RIV_FLUX",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "ALK": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ALK",
        "units": "meq/m^3",
        "description": "Alkalinity",
        "domain": "atmosphere",
        "component": "std"
    },
    "AOU": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "AOU",
        "units": "mmol/m^3",
        "description": "Apparent O2 Utilization",
        "domain": "atmosphere",
        "component": "std"
    },
    "ATM_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "ATM_ALT_CO2",
        "units": "ppmv",
        "description": "Atmospheric Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "ATM_BLACK_CARBON_FLUX_CPL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ATM_BLACK_CARBON_FLUX_CPL",
        "units": "g/cm^2/s",
        "description": "ATM_BLACK_CARBON_FLUX from cpl",
        "domain": "atmosphere",
        "component": "std"
    },
    "ATM_CO2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ATM_CO2",
        "units": "ppmv",
        "description": "Atmospheric CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "ATM_COARSE_DUST_FLUX_CPL": {
        "standard_name": "air_temperature",
        "cesm_name": "ATM_COARSE_DUST_FLUX_CPL",
        "units": "g/cm^2/s",
        "description": "ATM_COARSE_DUST_FLUX from cpl",
        "domain": "atmosphere",
        "component": "std"
    },
    "ATM_FINE_DUST_FLUX_CPL": {
        "standard_name": "air_temperature",
        "cesm_name": "ATM_FINE_DUST_FLUX_CPL",
        "units": "g/cm^2/s",
        "description": "ATM_FINE_DUST_FLUX from cpl",
        "domain": "atmosphere",
        "component": "std"
    },
    "BSF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "BSF",
        "units": "Sv",
        "description": "Diagnostic barotropic streamfunction",
        "domain": "atmosphere",
        "component": "std"
    },
    "bSi_form": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bSi_form",
        "units": "mmol/m^3/s",
        "description": "Total Si Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "bsiToSed": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "bsiToSed",
        "units": "nmol/cm^2/s",
        "description": "biogenic Si Flux to Sediments",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_FLUX_100m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CaCO3_FLUX_100m",
        "units": "mmol/m^3 cm/s",
        "description": "CaCO3 Flux at 100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_form_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "CaCO3_form_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Total CaCO3 Formation Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_form_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CaCO3_form_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Total CaCO3 Formation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_PROD_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "CaCO3_PROD_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of CaCO3 Production 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_PROD_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CaCO3_PROD_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of CaCO3 Production",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_REMIN_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "CaCO3_REMIN_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of CaCO3 Remineralization 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_REMIN_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CaCO3_REMIN_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of CaCO3 Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "calcToSed_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "calcToSed_ALT_CO2",
        "units": "nmol/cm^2/s",
        "description": "CaCO3 Flux to Sediments Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "calcToSed": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "calcToSed",
        "units": "nmol/cm^2/s",
        "description": "CaCO3 Flux to Sediments",
        "domain": "atmosphere",
        "component": "std"
    },
    "CFC11": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CFC11",
        "units": "fmol/cm^3",
        "description": "CFC11",
        "domain": "atmosphere",
        "component": "std"
    },
    "CFC12": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CFC12",
        "units": "fmol/cm^3",
        "description": "CFC12",
        "domain": "atmosphere",
        "component": "std"
    },
    "CO2STAR_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "CO2STAR_ALT_CO2",
        "units": "mmol/m^3",
        "description": "CO2 Star Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "CO2STAR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CO2STAR",
        "units": "mmol/m^3",
        "description": "CO2 Star",
        "domain": "atmosphere",
        "component": "std"
    },
    "co3_sat_calc": {
        "standard_name": "air_temperature",
        "cesm_name": "co3_sat_calc",
        "units": "mmol/m^3",
        "description": "CO3 concentration at calcite saturation",
        "domain": "atmosphere",
        "component": "std"
    },
    "CO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CO3",
        "units": "mmol/m^3",
        "description": "Carbonate Ion Concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "DENITRIF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DENITRIF",
        "units": "mmol/m^3/s",
        "description": "Denitrification",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIA_IMPVF_PO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIA_IMPVF_PO4",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIA_IMPVF_SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIA_IMPVF_SALT",
        "units": "gram/kilogram cm/s",
        "description": "SALT Flux Across Bottom Face from Diabatic Implicit Vertical Mixing",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIA_IMPVF_TEMP": {
        "standard_name": "air_temperature",
        "cesm_name": "DIA_IMPVF_TEMP",
        "units": "degC cm/s",
        "description": "TEMP Flux Across Bottom Face from Diabatic Implicit Vertical Mixing",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_agg_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_agg_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Aggregation Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_agg_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_agg_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Aggregation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_Fe_lim_surf": {
        "standard_name": "surface_temperature",
        "cesm_name": "diat_Fe_lim_surf",
        "units": "1",
        "description": "Diatom Fe Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "diatFe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diatFe",
        "units": "mmol/m^3",
        "description": "Diatom Iron",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_light_lim_surf": {
        "standard_name": "surface_temperature",
        "cesm_name": "diat_light_lim_surf",
        "units": "1",
        "description": "Diatom Light Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_loss_doc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_loss_doc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Loss to DOC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_loss_doc_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_loss_doc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Loss to DOC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_loss_poc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_loss_poc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Loss to POC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_loss_poc_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_loss_poc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Loss to POC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_loss_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_loss_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Loss Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_loss_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_loss_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Loss Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_N_lim_surf": {
        "standard_name": "surface_temperature",
        "cesm_name": "diat_N_lim_surf",
        "units": "1",
        "description": "Diatom N Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_P_lim_surf": {
        "standard_name": "surface_temperature",
        "cesm_name": "diat_P_lim_surf",
        "units": "1",
        "description": "Diatom P Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "diatP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diatP",
        "units": "mmol/m^3",
        "description": "Diatom Phosphorus",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_Qp": {
        "standard_name": "air_temperature",
        "cesm_name": "diat_Qp",
        "units": "1",
        "description": "Diatom P:C ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "diat_SiO3_lim_surf": {
        "standard_name": "surface_temperature",
        "cesm_name": "diat_SiO3_lim_surf",
        "units": "1",
        "description": "Diatom SiO3 Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "diatSi": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diatSi",
        "units": "mmol/m^3",
        "description": "Diatom Silicon",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_agg_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diaz_agg_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Aggregation Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_agg_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_agg_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Aggregation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diazC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diazC",
        "units": "mmol/m^3",
        "description": "Diazotroph Carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_Fe_lim_surf": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_Fe_lim_surf",
        "units": "1",
        "description": "Diazotroph Fe Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "diazFe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diazFe",
        "units": "mmol/m^3",
        "description": "Diazotroph Iron",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_light_lim_surf": {
        "standard_name": "surface_temperature",
        "cesm_name": "diaz_light_lim_surf",
        "units": "1",
        "description": "Diazotroph Light Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_loss_doc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diaz_loss_doc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Loss to DOC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_loss_doc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_loss_doc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Loss to DOC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_loss_poc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diaz_loss_poc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Loss to POC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_loss_poc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_loss_poc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Loss to POC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_loss_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "diaz_loss_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Loss Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_loss_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_loss_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Loss Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_Nfix": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_Nfix",
        "units": "mmol/m^3/s",
        "description": "Diazotroph N Fixation",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_P_lim_surf": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diaz_P_lim_surf",
        "units": "1",
        "description": "Diazotroph P Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "diazP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "diazP",
        "units": "mmol/m^3",
        "description": "Diazotroph Phosphorus",
        "domain": "atmosphere",
        "component": "std"
    },
    "diaz_Qp": {
        "standard_name": "specific_humidity",
        "cesm_name": "diaz_Qp",
        "units": "1",
        "description": "Diazotroph P:C ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIC_ALT_CO2_RIV_FLUX": {
        "standard_name": "air_temperature",
        "cesm_name": "DIC_ALT_CO2_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Alternative CO2 Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "DIC_ALT_CO2",
        "units": "mmol/m^3",
        "description": "Dissolved Inorganic Carbon Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIC_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIC_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIC",
        "units": "mmol/m^3",
        "description": "Dissolved Inorganic Carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOC_prod": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOC_prod",
        "units": "mmol/m^3/s",
        "description": "DOC Production",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOC_prod_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "DOC_prod_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of DOC Production 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOC_prod_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOC_prod_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of DOC Production",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOC_remin_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "DOC_remin_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of DOC Remineralization 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOC_remin_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOC_remin_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of DOC Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOC_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOC_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Organic Carbon Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOCr_remin_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "DOCr_remin_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of DOCr Remineralization 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOCr_remin_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOCr_remin_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of DOCr Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOCr_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOCr_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Refractory DOC Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOCr",
        "units": "mmol/m^3",
        "description": "Refractory DOC",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOC",
        "units": "mmol/m^3",
        "description": "Dissolved Organic Carbon",
        "domain": "atmosphere",
        "component": "std"
    },
    "DON_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DON_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Organic Nitrogen Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DONr_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DONr_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Refractory DON Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DONr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DONr",
        "units": "mmol/m^3",
        "description": "Refractory DON",
        "domain": "atmosphere",
        "component": "std"
    },
    "DON": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DON",
        "units": "mmol/m^3",
        "description": "Dissolved Organic Nitrogen",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOP_diat_uptake": {
        "standard_name": "air_temperature",
        "cesm_name": "DOP_diat_uptake",
        "units": "mmol/m^3/s",
        "description": "Diatom DOP Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOP_diaz_uptake": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOP_diaz_uptake",
        "units": "mmol/m^3/s",
        "description": "Diazotroph DOP Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOP_remin": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOP_remin",
        "units": "mmol/m^3/s",
        "description": "DOP Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOP_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOP_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Organic Phosphorus Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOPr_remin": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOPr_remin",
        "units": "mmol/m^3/s",
        "description": "DOPr Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOPr_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOPr_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Refractory DOP Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOPr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOPr",
        "units": "mmol/m^3",
        "description": "Refractory DOP",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOP_sp_uptake": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOP_sp_uptake",
        "units": "mmol/m^3/s",
        "description": "Small Phyto DOP Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOP",
        "units": "mmol/m^3",
        "description": "Dissolved Organic Phosphorus",
        "domain": "atmosphere",
        "component": "std"
    },
    "dust_FLUX_IN": {
        "standard_name": "air_temperature",
        "cesm_name": "dust_FLUX_IN",
        "units": "g/cm^2/s",
        "description": "Dust Flux into Cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "dust_REMIN": {
        "standard_name": "air_temperature",
        "cesm_name": "dust_REMIN",
        "units": "g/cm^3/s",
        "description": "Dust Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "dustToSed": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "dustToSed",
        "units": "g/cm^2/s",
        "description": "dust Flux to Sediments",
        "domain": "atmosphere",
        "component": "std"
    },
    "ECOSYS_IFRAC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ECOSYS_IFRAC",
        "units": "fraction",
        "description": "Ice Fraction for ecosys fluxes",
        "domain": "atmosphere",
        "component": "std"
    },
    "EVAP_F": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "EVAP_F",
        "units": "kg/m^2/s",
        "description": "Evaporation Flux from Coupler",
        "domain": "atmosphere",
        "component": "std"
    },
    "Fefree": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Fefree",
        "units": "mmol/m^3",
        "description": "Fe not bound to Ligand",
        "domain": "atmosphere",
        "component": "std"
    },
    "Fe_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Fe_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Iron Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Fe",
        "units": "mmol/m^3",
        "description": "Dissolved Inorganic Iron",
        "domain": "atmosphere",
        "component": "std"
    },
    "FG_ABIO_DIC14": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FG_ABIO_DIC14",
        "units": "nmol/cm^2/s",
        "description": "Surface gas flux of abiotic DIC14",
        "domain": "atmosphere",
        "component": "std"
    },
    "FG_ABIO_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FG_ABIO_DIC",
        "units": "nmol/cm^2/s",
        "description": "Surface gas flux of abiotic DIC",
        "domain": "atmosphere",
        "component": "std"
    },
    "FRACR_BIN_01": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FRACR_BIN_01",
        "units": "1",
        "description": "fraction of ocean cell occupied by mcog bin 01 for radiative terms",
        "domain": "atmosphere",
        "component": "std"
    },
    "FRACR_BIN_02": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FRACR_BIN_02",
        "units": "1",
        "description": "fraction of ocean cell occupied by mcog bin 02 for radiative terms",
        "domain": "atmosphere",
        "component": "std"
    },
    "FRACR_BIN_03": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FRACR_BIN_03",
        "units": "1",
        "description": "fraction of ocean cell occupied by mcog bin 03 for radiative terms",
        "domain": "atmosphere",
        "component": "std"
    },
    "FRACR_BIN_04": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FRACR_BIN_04",
        "units": "1",
        "description": "fraction of ocean cell occupied by mcog bin 04 for radiative terms",
        "domain": "atmosphere",
        "component": "std"
    },
    "FRACR_BIN_05": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FRACR_BIN_05",
        "units": "1",
        "description": "fraction of ocean cell occupied by mcog bin 05 for radiative terms",
        "domain": "atmosphere",
        "component": "std"
    },
    "FRACR_BIN_06": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FRACR_BIN_06",
        "units": "1",
        "description": "fraction of ocean cell occupied by mcog bin 06 for radiative terms",
        "domain": "atmosphere",
        "component": "std"
    },
    "FvICE_ABIO_DIC14": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FvICE_ABIO_DIC14",
        "units": "nmol/cm^2/s",
        "description": "ABIO_DIC14 Virtual Surface Flux ICE",
        "domain": "atmosphere",
        "component": "std"
    },
    "FvICE_ABIO_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FvICE_ABIO_DIC",
        "units": "nmol/cm^2/s",
        "description": "ABIO_DIC Virtual Surface Flux ICE",
        "domain": "atmosphere",
        "component": "std"
    },
    "FvICE_ALK_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "FvICE_ALK_ALT_CO2",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Alternative CO2 Virtual Surface Flux ICE",
        "domain": "atmosphere",
        "component": "std"
    },
    "FvICE_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "FvICE_DIC_ALT_CO2",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Alternative CO2 Virtual Surface Flux ICE",
        "domain": "atmosphere",
        "component": "std"
    },
    "FvPER_ABIO_DIC14": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FvPER_ABIO_DIC14",
        "units": "nmol/cm^2/s",
        "description": "ABIO_DIC14 Virtual Surface Flux PER",
        "domain": "atmosphere",
        "component": "std"
    },
    "FvPER_ABIO_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "FvPER_ABIO_DIC",
        "units": "nmol/cm^2/s",
        "description": "ABIO_DIC Virtual Surface Flux PER",
        "domain": "atmosphere",
        "component": "std"
    },
    "FvPER_ALK_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "FvPER_ALK_ALT_CO2",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Alternative CO2 Virtual Surface Flux PER",
        "domain": "atmosphere",
        "component": "std"
    },
    "FvPER_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "FvPER_DIC_ALT_CO2",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Alternative CO2 Virtual Surface Flux PER",
        "domain": "atmosphere",
        "component": "std"
    },
    "GRADX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GRADX",
        "units": "centimeter/s^2",
        "description": "Horizontal press. grad. in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "GRADY": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "GRADY",
        "units": "centimeter/s^2",
        "description": "Horizontal press. grad. in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat_doc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diat_doc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Grazing to DOC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat_doc_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diat_doc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Grazing to DOC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat_poc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diat_poc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Grazing to POC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat_poc_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diat_poc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Grazing to POC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diat_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Grazing Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diat_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Grazing Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat_zoo_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diat_zoo_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Grazing to ZOO Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diat_zoo_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diat_zoo_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom Grazing to ZOO Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz_doc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diaz_doc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Grazing to DOC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz_doc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_diaz_doc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Grazing to DOC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz_poc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diaz_poc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Grazing to POC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz_poc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_diaz_poc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Grazing to POC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diaz_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Grazing Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_diaz_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Grazing Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz_zoo_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_diaz_zoo_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Grazing to ZOO Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_diaz_zoo_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_diaz_zoo_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph Grazing to ZOO Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp_doc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_sp_doc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Grazing to DOC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp_doc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_sp_doc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Grazing to DOC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp_poc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_sp_poc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Grazing to POC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp_poc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_sp_poc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Grazing to POC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_sp_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Grazing Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_sp_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Grazing Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp_zoo_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "graze_sp_zoo_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Grazing to ZOO Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_sp_zoo_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_sp_zoo_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Grazing to ZOO Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "HCO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HCO3",
        "units": "mmol/m^3",
        "description": "Bicarbonate Ion Concentration",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFE_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "HDIFE_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "DIC_ALT_CO2 Horizontal Diffusive Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFE_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFE_DIC",
        "units": "mmol/m^3/s",
        "description": "DIC Horizontal Diffusive Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFE_PO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFE_PO4",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFFU": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFFU",
        "units": "centimeter/s^2",
        "description": "Horizontal diffusion in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFFV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFFV",
        "units": "centimeter/s^2",
        "description": "Horizontal diffusion in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFN_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "HDIFN_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "DIC_ALT_CO2 Horizontal Diffusive Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFN_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFN_DIC",
        "units": "mmol/m^3/s",
        "description": "DIC Horizontal Diffusive Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFN_PO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFN_PO4",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFT",
        "units": "centimeter degC/s",
        "description": "Vertically Integrated Horz Mix T tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "HMXL_DR2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HMXL_DR2",
        "units": "centimeter^2",
        "description": "Mixed-Layer Depth squared (density)",
        "domain": "atmosphere",
        "component": "std"
    },
    "HMXL_DR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HMXL_DR",
        "units": "centimeter",
        "description": "Mixed-Layer Depth (density)",
        "domain": "atmosphere",
        "component": "std"
    },
    "HMXL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HMXL",
        "units": "centimeter",
        "description": "Mixed-Layer Depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "HOR_DIFF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HOR_DIFF",
        "units": "cm^2/s",
        "description": "Horizontal diffusion coefficient",
        "domain": "atmosphere",
        "component": "std"
    },
    "IAGE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "IAGE",
        "units": "years",
        "description": "Ideal Age",
        "domain": "atmosphere",
        "component": "std"
    },
    "IFRAC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "IFRAC",
        "units": "fraction",
        "description": "Ice Fraction from Coupler",
        "domain": "atmosphere",
        "component": "std"
    },
    "insitu_temp": {
        "standard_name": "air_temperature",
        "cesm_name": "insitu_temp",
        "units": "degC",
        "description": "in situ temperature",
        "domain": "atmosphere",
        "component": "std"
    },
    "IOFF_F": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "IOFF_F",
        "units": "kg/m^2/s",
        "description": "Ice Runoff Flux from Coupler due to Land-Model Snow Capping",
        "domain": "atmosphere",
        "component": "std"
    },
    "ISOP_ADV_TEND_SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ISOP_ADV_TEND_SALT",
        "units": "gram/kilogram/s",
        "description": "Eddy-induced advective tendency for SALT",
        "domain": "atmosphere",
        "component": "std"
    },
    "ISOP_ADV_TEND_TEMP": {
        "standard_name": "air_temperature",
        "cesm_name": "ISOP_ADV_TEND_TEMP",
        "units": "degC/s",
        "description": "Eddy-induced advective tendency for TEMP",
        "domain": "atmosphere",
        "component": "std"
    },
    "J_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "J_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Carbon Alternative CO2 Source Sink Term",
        "domain": "atmosphere",
        "component": "std"
    },
    "J_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "J_DIC",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Carbon Source Sink Term",
        "domain": "atmosphere",
        "component": "std"
    },
    "Jint_100m_ALK_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_ALK_ALT_CO2",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Alternative CO2 Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "Jint_100m_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_DIC_ALT_CO2",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Carbon Alternative CO2 Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "Jint_100m_DOCr": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_100m_DOCr",
        "units": "mmol/m^3 cm/s",
        "description": "Refractory DOC Source Sink Term Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "Jint_ABIO_DIC14": {
        "standard_name": "air_temperature",
        "cesm_name": "Jint_ABIO_DIC14",
        "units": "nmol/cm^2/s",
        "description": "ABIO_DIC14 Source Sink Term Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "KAPPA_ISOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "KAPPA_ISOP",
        "units": "cm^2/s",
        "description": "Isopycnal diffusion coefficient",
        "domain": "atmosphere",
        "component": "std"
    },
    "KAPPA_THIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "KAPPA_THIC",
        "units": "cm^2/s",
        "description": "Thickness diffusion coefficient",
        "domain": "atmosphere",
        "component": "std"
    },
    "KVMIX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "KVMIX",
        "units": "centimeter^2/s",
        "description": "Vertical diabatic diffusivity due to Tidal Mixing+background",
        "domain": "atmosphere",
        "component": "std"
    },
    "Lig_deg": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Lig_deg",
        "units": "mmol/m^3/s",
        "description": "Loss of Fe-binding Ligand from Bacterial Degradation",
        "domain": "atmosphere",
        "component": "std"
    },
    "Lig_loss": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Lig_loss",
        "units": "mmol/m^3/s",
        "description": "Loss of Fe-binding Ligand",
        "domain": "atmosphere",
        "component": "std"
    },
    "Lig_photochem": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Lig_photochem",
        "units": "mmol/m^3/s",
        "description": "Loss of Fe-binding Ligand from UV radiation",
        "domain": "atmosphere",
        "component": "std"
    },
    "Lig_prod": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Lig_prod",
        "units": "mmol/m^3/s",
        "description": "Production of Fe-binding Ligand",
        "domain": "atmosphere",
        "component": "std"
    },
    "Lig_scavenge": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Lig_scavenge",
        "units": "mmol/m^3/s",
        "description": "Loss of Fe-binding Ligand from Scavenging",
        "domain": "atmosphere",
        "component": "std"
    },
    "Lig": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Lig",
        "units": "mmol/m^3",
        "description": "Iron Binding Ligand",
        "domain": "atmosphere",
        "component": "std"
    },
    "LWDN_F": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LWDN_F",
        "units": "watt/m^2",
        "description": "Longwave Heat Flux (dn) from Coupler",
        "domain": "atmosphere",
        "component": "std"
    },
    "LWUP_F": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "LWUP_F",
        "units": "watt/m^2",
        "description": "Longwave Heat Flux (up) from Coupler",
        "domain": "atmosphere",
        "component": "std"
    },
    "MOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "MOC",
        "units": "Sverdrups",
        "description": "Meridional Overturning Circulation",
        "domain": "atmosphere",
        "component": "std"
    },
    "NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NH4",
        "units": "mmol/m^3",
        "description": "Dissolved Ammonia",
        "domain": "atmosphere",
        "component": "std"
    },
    "N_HEAT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "N_HEAT",
        "units": "Pwatt",
        "description": "Northward Heat Transport",
        "domain": "atmosphere",
        "component": "std"
    },
    "NHx_SURFACE_EMIS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NHx_SURFACE_EMIS",
        "units": "nmol/cm^2/s",
        "description": "Emission of NHx to Atmosphere",
        "domain": "atmosphere",
        "component": "std"
    },
    "NITRIF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NITRIF",
        "units": "mmol/m^3/s",
        "description": "Nitrification",
        "domain": "atmosphere",
        "component": "std"
    },
    "NO3_RESTORE_TEND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NO3_RESTORE_TEND",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Nitrate Restoring Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "NO3_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NO3_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Nitrate Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "NOx_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "NOx_FLUX",
        "units": "nmol/cm^2/s",
        "description": "Flux of NOx from Atmosphere",
        "domain": "atmosphere",
        "component": "std"
    },
    "O2_ZMIN_DEPTH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "O2_ZMIN_DEPTH",
        "units": "cm",
        "description": "Depth of Vertical Minimum of O2",
        "domain": "atmosphere",
        "component": "std"
    },
    "O2_ZMIN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "O2_ZMIN",
        "units": "mmol/m^3",
        "description": "Vertical Minimum of O2",
        "domain": "atmosphere",
        "component": "std"
    },
    "pfeToSed": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pfeToSed",
        "units": "nmol/cm^2/s",
        "description": "pFe Flux to Sediments",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_diat_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_diat_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom C Fixation Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_diat_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_diat_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diatom C Fixation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_diaz_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_diaz_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph C Fixation Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_diaz_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoC_diaz_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Diazotroph C Fixation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_NO3_TOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoC_NO3_TOT",
        "units": "mmol/m^3/s",
        "description": "Total C Fixation from NO3",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_NO3_TOT_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_NO3_TOT_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Total C Fixation from NO3 Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_NO3_TOT_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_NO3_TOT_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Total C Fixation from NO3 Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_sp_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_sp_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto C Fixation Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_sp_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoC_sp_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto C Fixation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_TOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoC_TOT",
        "units": "mmol/m^3/s",
        "description": "Total C Fixation",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_TOT_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_TOT_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Total C Fixation Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoC_TOT_zint": {
        "standard_name": "air_temperature",
        "cesm_name": "photoC_TOT_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Total C Fixation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoFe_diat": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoFe_diat",
        "units": "mmol/m^3/s",
        "description": "Diatom Fe Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoFe_diaz": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoFe_diaz",
        "units": "mmol/m^3/s",
        "description": "Diazotroph Fe Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoFe_sp": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoFe_sp",
        "units": "mmol/m^3/s",
        "description": "Small Phyto Fe Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoNH4_diat": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoNH4_diat",
        "units": "mmol/m^3/s",
        "description": "Diatom NH4 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoNH4_diaz": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoNH4_diaz",
        "units": "mmol/m^3/s",
        "description": "Diazotroph NH4 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoNH4_sp": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoNH4_sp",
        "units": "mmol/m^3/s",
        "description": "Small Phyto NH4 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoNO3_diat": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoNO3_diat",
        "units": "mmol/m^3/s",
        "description": "Diatom NO3 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoNO3_diaz": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoNO3_diaz",
        "units": "mmol/m^3/s",
        "description": "Diazotroph NO3 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "photoNO3_sp": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "photoNO3_sp",
        "units": "mmol/m^3/s",
        "description": "Small Phyto NO3 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "PH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PH",
        "units": "1",
        "description": "Surface pH",
        "domain": "atmosphere",
        "component": "std"
    },
    "P_iron_FLUX_100m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "P_iron_FLUX_100m",
        "units": "mmol/m^3 cm/s",
        "description": "P_iron Flux at 100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "P_iron_REMIN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "P_iron_REMIN",
        "units": "mmol/m^3/s",
        "description": "P_iron Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "PO4_diat_uptake": {
        "standard_name": "air_temperature",
        "cesm_name": "PO4_diat_uptake",
        "units": "mmol/m^3/s",
        "description": "Diatom PO4 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "PO4_diaz_uptake": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PO4_diaz_uptake",
        "units": "mmol/m^3/s",
        "description": "Diazotroph PO4 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "PO4_RESTORE_TEND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PO4_RESTORE_TEND",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Phosphate Restoring Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "PO4_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PO4_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Phosphate Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "PO4_sp_uptake": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PO4_sp_uptake",
        "units": "mmol/m^3/s",
        "description": "Small Phyto PO4 Uptake",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_FLUX_100m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_FLUX_100m",
        "units": "mmol/m^3 cm/s",
        "description": "POC Flux at 100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_FLUX_IN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_FLUX_IN",
        "units": "mmol/m^3 cm/s",
        "description": "POC Flux into Cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_PROD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_PROD",
        "units": "mmol/m^3/s",
        "description": "POC Production",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_PROD_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "POC_PROD_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of POC Production 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_PROD_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_PROD_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of POC Production",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_REMIN_DIC_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "POC_REMIN_DIC_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of POC Remineralization routed to DIC 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_REMIN_DIC_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_REMIN_DIC_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of POC Remineralization routed to DIC",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_REMIN_DOCr_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "POC_REMIN_DOCr_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of POC Remineralization routed to DOCr 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_REMIN_DOCr_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_REMIN_DOCr_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Vertical Integral of POC Remineralization routed to DOCr",
        "domain": "atmosphere",
        "component": "std"
    },
    "pocToSed": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "pocToSed",
        "units": "nmol/cm^2/s",
        "description": "POC Flux to Sediments",
        "domain": "atmosphere",
        "component": "std"
    },
    "ponToSed": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ponToSed",
        "units": "nmol/cm^2/s",
        "description": "nitrogen burial Flux to Sediments",
        "domain": "atmosphere",
        "component": "std"
    },
    "POP_FLUX_100m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POP_FLUX_100m",
        "units": "mmol/m^3 cm/s",
        "description": "POP Flux at 100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "POP_FLUX_IN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POP_FLUX_IN",
        "units": "mmol/m^3 cm/s",
        "description": "POP Flux into Cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "POP_PROD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POP_PROD",
        "units": "mmol/m^3/s",
        "description": "POP Production",
        "domain": "atmosphere",
        "component": "std"
    },
    "POP_REMIN_DOPr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POP_REMIN_DOPr",
        "units": "mmol/m^3/s",
        "description": "POP Remineralization routed to DOPr",
        "domain": "atmosphere",
        "component": "std"
    },
    "POP_REMIN_PO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POP_REMIN_PO4",
        "units": "mmol/m^3/s",
        "description": "POP Remineralization routed to PO4",
        "domain": "atmosphere",
        "component": "std"
    },
    "popToSed": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "popToSed",
        "units": "nmol/cm^2/s",
        "description": "phosphorus Flux to Sediments",
        "domain": "atmosphere",
        "component": "std"
    },
    "PREC_F": {
        "standard_name": "precipitation_flux",
        "cesm_name": "PREC_F",
        "units": "kg/m^2/s",
        "description": "Precipitation Flux from Cpl (rain+snow)",
        "domain": "atmosphere",
        "component": "std"
    },
    "PV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PV",
        "units": "1/s/cm",
        "description": "Potential Vorticity",
        "domain": "atmosphere",
        "component": "std"
    },
    "QFLUX": {
        "standard_name": "specific_humidity",
        "cesm_name": "QFLUX",
        "units": "Watts/meter^2",
        "description": "Internal Ocean Heat Flux Due to Ice Formation; heat of fusion > 0 or ice-melting potential < 0",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSW_3D": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_3D",
        "units": "watt/m^2",
        "description": "Solar Short-Wave Heat Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSW_BIN_01": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_BIN_01",
        "units": "W m-2",
        "description": "net shortwave into mcog bin 01",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSW_BIN_02": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_BIN_02",
        "units": "W m-2",
        "description": "net shortwave into mcog bin 02",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSW_BIN_03": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_BIN_03",
        "units": "W m-2",
        "description": "net shortwave into mcog bin 03",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSW_BIN_04": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_BIN_04",
        "units": "W m-2",
        "description": "net shortwave into mcog bin 04",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSW_BIN_05": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_BIN_05",
        "units": "W m-2",
        "description": "net shortwave into mcog bin 05",
        "domain": "atmosphere",
        "component": "std"
    },
    "QSW_BIN_06": {
        "standard_name": "specific_humidity",
        "cesm_name": "QSW_BIN_06",
        "units": "W m-2",
        "description": "net shortwave into mcog bin 06",
        "domain": "atmosphere",
        "component": "std"
    },
    "Redi_TEND_SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "Redi_TEND_SALT",
        "units": "gram/kilogram/s",
        "description": "Redi tendency for SALT",
        "domain": "atmosphere",
        "component": "std"
    },
    "Redi_TEND_TEMP": {
        "standard_name": "air_temperature",
        "cesm_name": "Redi_TEND_TEMP",
        "units": "degC/s",
        "description": "Redi tendency for TEMP",
        "domain": "atmosphere",
        "component": "std"
    },
    "RESID_T": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RESID_T",
        "units": "watt/m^2",
        "description": "Free-Surface Residual Flux (T)",
        "domain": "atmosphere",
        "component": "std"
    },
    "RF_TEND_SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RF_TEND_SALT",
        "units": "gram/kilogram/s",
        "description": "Robert Filter Tendency for SALT",
        "domain": "atmosphere",
        "component": "std"
    },
    "RF_TEND_TEMP": {
        "standard_name": "air_temperature",
        "cesm_name": "RF_TEND_TEMP",
        "units": "degC/s",
        "description": "Robert Filter Tendency for TEMP",
        "domain": "atmosphere",
        "component": "std"
    },
    "RHO": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RHO",
        "units": "gram/centimeter^3",
        "description": "In-Situ Density",
        "domain": "atmosphere",
        "component": "std"
    },
    "RHO_VINT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RHO_VINT",
        "units": "gram/centimeter^2",
        "description": "Vertical Integral of In-Situ Density",
        "domain": "atmosphere",
        "component": "std"
    },
    "ROFF_F": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "ROFF_F",
        "units": "kg/m^2/s",
        "description": "Runoff Flux from Coupler",
        "domain": "atmosphere",
        "component": "std"
    },
    "SEAICE_BLACK_CARBON_FLUX_CPL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SEAICE_BLACK_CARBON_FLUX_CPL",
        "units": "g/cm^2/s",
        "description": "SEAICE_BLACK_CARBON_FLUX from cpl",
        "domain": "atmosphere",
        "component": "std"
    },
    "SEAICE_DUST_FLUX_CPL": {
        "standard_name": "air_temperature",
        "cesm_name": "SEAICE_DUST_FLUX_CPL",
        "units": "g/cm^2/s",
        "description": "SEAICE_DUST_FLUX from cpl",
        "domain": "atmosphere",
        "component": "std"
    },
    "SedDenitrif": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SedDenitrif",
        "units": "nmol/cm^2/s",
        "description": "nitrogen loss in Sediments",
        "domain": "atmosphere",
        "component": "std"
    },
    "SF6_ATM_PRESS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SF6_ATM_PRESS",
        "units": "atmospheres",
        "description": "Atmospheric Pressure for SF6 fluxes",
        "domain": "atmosphere",
        "component": "std"
    },
    "SF6_IFRAC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SF6_IFRAC",
        "units": "fraction",
        "description": "Ice Fraction for SF6 fluxes",
        "domain": "atmosphere",
        "component": "std"
    },
    "SF6": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SF6",
        "units": "fmol/cm^3",
        "description": "SF6",
        "domain": "atmosphere",
        "component": "std"
    },
    "SF6_XKW": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SF6_XKW",
        "units": "cm/s",
        "description": "XKW for SF6 fluxes",
        "domain": "atmosphere",
        "component": "std"
    },
    "S_FLUX_EXCH_INTRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "S_FLUX_EXCH_INTRF",
        "units": "g/kg*cm/s",
        "description": "Vertical Salt Flux Across Upper/Lower Layer Interface (FromEBM)",
        "domain": "atmosphere",
        "component": "std"
    },
    "S_FLUX_ROFF_VSF_SRF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "S_FLUX_ROFF_VSF_SRF",
        "units": "g/kg*cm/s",
        "description": "Surface Salt Virtual Salt Flux Associated with Rivers",
        "domain": "atmosphere",
        "component": "std"
    },
    "SFWF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SFWF",
        "units": "kg/m^2/s",
        "description": "Virtual Salt Flux in FW Flux formulation",
        "domain": "atmosphere",
        "component": "std"
    },
    "SHF_QSW": {
        "standard_name": "specific_humidity",
        "cesm_name": "SHF_QSW",
        "units": "watt/m^2",
        "description": "Solar Short-Wave Heat Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SHF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SHF",
        "units": "watt/m^2",
        "description": "Total Surface Heat Flux Including SW",
        "domain": "atmosphere",
        "component": "std"
    },
    "SiO2_FLUX_100m": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SiO2_FLUX_100m",
        "units": "mmol/m^3 cm/s",
        "description": "SiO2 Flux at 100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "SiO2_PROD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SiO2_PROD",
        "units": "mmol/m^3/s",
        "description": "SiO2 Production",
        "domain": "atmosphere",
        "component": "std"
    },
    "SiO3_RESTORE_TEND": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SiO3_RESTORE_TEND",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Silicate Restoring Tendency",
        "domain": "atmosphere",
        "component": "std"
    },
    "SiO3_RIV_FLUX": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SiO3_RIV_FLUX",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Silicate Riverine Flux",
        "domain": "atmosphere",
        "component": "std"
    },
    "SiO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SiO3",
        "units": "mmol/m^3",
        "description": "Dissolved Inorganic Silicate",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_agg_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "sp_agg_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Aggregation Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_agg_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_agg_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Aggregation Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "spCaCO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "spCaCO3",
        "units": "mmol/m^3",
        "description": "Small Phyto CaCO3",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_Fe_lim_surf": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_Fe_lim_surf",
        "units": "1",
        "description": "Small Phyto Fe Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "spFe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "spFe",
        "units": "mmol/m^3",
        "description": "Small Phyto Iron",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_light_lim_surf": {
        "standard_name": "surface_temperature",
        "cesm_name": "sp_light_lim_surf",
        "units": "1",
        "description": "Small Phyto Light Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_loss_doc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "sp_loss_doc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Loss to DOC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_loss_doc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_loss_doc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Loss to DOC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_loss_poc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "sp_loss_poc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Loss to POC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_loss_poc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_loss_poc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Loss to POC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_loss_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "sp_loss_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Loss Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_loss_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_loss_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Small Phyto Loss Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_N_lim_surf": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_N_lim_surf",
        "units": "1",
        "description": "Small Phyto N Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_P_lim_surf": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "sp_P_lim_surf",
        "units": "1",
        "description": "Small Phyto P Limitation Surface",
        "domain": "atmosphere",
        "component": "std"
    },
    "spP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "spP",
        "units": "mmol/m^3",
        "description": "Small Phyto Phosphorus",
        "domain": "atmosphere",
        "component": "std"
    },
    "sp_Qp": {
        "standard_name": "specific_humidity",
        "cesm_name": "sp_Qp",
        "units": "1",
        "description": "Small Phyto P:C ratio",
        "domain": "atmosphere",
        "component": "std"
    },
    "SSH": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SSH",
        "units": "centimeter",
        "description": "Sea Surface Height",
        "domain": "atmosphere",
        "component": "std"
    },
    "SSS2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SSS2",
        "units": "(gram/kilogram)**2",
        "description": "Sea Surface Salinity**2",
        "domain": "atmosphere",
        "component": "std"
    },
    "STF_ABIO_DIC14": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STF_ABIO_DIC14",
        "units": "nmol/cm^2/s",
        "description": "ABIO_DIC14 Surface Flux excludes FvICE term",
        "domain": "atmosphere",
        "component": "std"
    },
    "STF_ABIO_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STF_ABIO_DIC",
        "units": "nmol/cm^2/s",
        "description": "ABIO_DIC Surface Flux excludes FvICE term",
        "domain": "atmosphere",
        "component": "std"
    },
    "STF_ALK_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "STF_ALK_ALT_CO2",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Alternative CO2 Surface Flux excludes FvICE term",
        "domain": "atmosphere",
        "component": "std"
    },
    "STF_ALK": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STF_ALK",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Surface Flux excludes FvICE term",
        "domain": "atmosphere",
        "component": "std"
    },
    "STF_SF6": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "STF_SF6",
        "units": "fmol/cm^2/s",
        "description": "SF6 Surface Flux excludes FvICE term",
        "domain": "atmosphere",
        "component": "std"
    },
    "SUBM_ADV_TEND_SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SUBM_ADV_TEND_SALT",
        "units": "gram/kilogram/s",
        "description": "Submeso advective tendency for SALT",
        "domain": "atmosphere",
        "component": "std"
    },
    "SUBM_ADV_TEND_TEMP": {
        "standard_name": "air_temperature",
        "cesm_name": "SUBM_ADV_TEND_TEMP",
        "units": "degC/s",
        "description": "Submeso advective tendency for TEMP",
        "domain": "atmosphere",
        "component": "std"
    },
    "SU": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SU",
        "units": "centimeter^2/s",
        "description": "Vertically Integrated Velocity in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "SV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "SV",
        "units": "centimeter^2/s",
        "description": "Vertically Integrated Velocity in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUX2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUX2",
        "units": "dyne^2/centimeter^4",
        "description": "Windstress**2 in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "TAUY2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TAUY2",
        "units": "dyne^2/centimeter^4",
        "description": "Windstress**2 in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEMP2": {
        "standard_name": "air_temperature",
        "cesm_name": "TEMP2",
        "units": "degC^2",
        "description": "Temperature**2",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEND_SALT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TEND_SALT",
        "units": "gram/kilogram/s",
        "description": "Tendency of Thickness Weighted SALT",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEND_TEMP": {
        "standard_name": "air_temperature",
        "cesm_name": "TEND_TEMP",
        "units": "degC/s",
        "description": "Tendency of Thickness Weighted TEMP",
        "domain": "atmosphere",
        "component": "std"
    },
    "tend_zint_100m_ALK_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_ALK_ALT_CO2",
        "units": "meq/m^3 cm/s",
        "description": "Alkalinity Alternative CO2 Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "tend_zint_100m_DOCr": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_DOCr",
        "units": "mmol/m^3 cm/s",
        "description": "Refractory DOC Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "tend_zint_100m_SiO3": {
        "standard_name": "air_temperature",
        "cesm_name": "tend_zint_100m_SiO3",
        "units": "mmol/m^3 cm/s",
        "description": "Dissolved Inorganic Silicate Tendency Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "T_FLUX_EXCH_INTRF": {
        "standard_name": "air_temperature",
        "cesm_name": "T_FLUX_EXCH_INTRF",
        "units": "degC*cm/s",
        "description": "Vertical Temperature Flux Across Upper/Lower Layer Interface (From EBM)",
        "domain": "atmosphere",
        "component": "std"
    },
    "TIDAL_DIFF": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TIDAL_DIFF",
        "units": "no units",
        "description": "Jayne Tidal Diffusion",
        "domain": "atmosphere",
        "component": "std"
    },
    "TMXL_DR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TMXL_DR",
        "units": "centimeter",
        "description": "Minimum Mixed-Layer Depth (density)",
        "domain": "atmosphere",
        "component": "std"
    },
    "UE_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "UE_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "DIC_ALT_CO2 Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "UE_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UE_DIC",
        "units": "mmol/m^3/s",
        "description": "DIC Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "UE_PO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UE_PO4",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "UES": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UES",
        "units": "gram/kilogram/s",
        "description": "Salt Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "UET": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UET",
        "units": "degC/s",
        "description": "Flux of Heat in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "UVEL2": {
        "standard_name": "eastward_wind",
        "cesm_name": "UVEL2",
        "units": "centimeter^2/s^2",
        "description": "Velocity**2 in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VDC_T": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VDC_T",
        "units": "cm^2/s",
        "description": "total diabatic vertical TEMP diffusivity",
        "domain": "atmosphere",
        "component": "std"
    },
    "VDIFFU": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VDIFFU",
        "units": "centimeter/s^2",
        "description": "Vertical diffusion in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VDIFFV": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VDIFFV",
        "units": "centimeter/s^2",
        "description": "Vertical diffusion in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VN_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "VN_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "DIC_ALT_CO2 Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VN_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VN_DIC",
        "units": "mmol/m^3/s",
        "description": "DIC Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VN_PO4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VN_PO4",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "VNS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VNS",
        "units": "gram/kilogram/s",
        "description": "Salt Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VNT_ISOP": {
        "standard_name": "air_temperature",
        "cesm_name": "VNT_ISOP",
        "units": "degC/s",
        "description": "Heat Flux Tendency in grid-y Dir due to Eddy-Induced Vel (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "VNT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VNT",
        "units": "degC/s",
        "description": "Flux of Heat in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VVEL2": {
        "standard_name": "northward_wind",
        "cesm_name": "VVEL2",
        "units": "centimeter^2/s^2",
        "description": "Velocity**2 in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "WISOP": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WISOP",
        "units": "cm/s",
        "description": "Vertical Bolus Velocity (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "WSUBM": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WSUBM",
        "units": "cm/s",
        "description": "Vertical submeso velocity (diagnostic)",
        "domain": "atmosphere",
        "component": "std"
    },
    "WT_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "WT_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "DIC_ALT_CO2 Flux Across Top Face",
        "domain": "atmosphere",
        "component": "std"
    },
    "WT_DIC": {
        "standard_name": "air_temperature",
        "cesm_name": "WT_DIC",
        "units": "mmol/m^3/s",
        "description": "DIC Flux Across Top Face",
        "domain": "atmosphere",
        "component": "std"
    },
    "WT_PO4": {
        "standard_name": "air_temperature",
        "cesm_name": "WT_PO4",
        "units": "UNKNOWN",
        "description": "UNKNOWN",
        "domain": "atmosphere",
        "component": "std"
    },
    "WTS": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WTS",
        "units": "gram/kilogram/s",
        "description": "Salt Flux Across Top Face",
        "domain": "atmosphere",
        "component": "std"
    },
    "WTT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "WTT",
        "units": "degC/s",
        "description": "Heat Flux Across Top Face",
        "domain": "atmosphere",
        "component": "std"
    },
    "XMXL_DR": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "XMXL_DR",
        "units": "centimeter",
        "description": "Maximum Mixed-Layer Depth (density)",
        "domain": "atmosphere",
        "component": "std"
    },
    "XMXL": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "XMXL",
        "units": "centimeter",
        "description": "Maximum Mixed-Layer Depth",
        "domain": "atmosphere",
        "component": "std"
    },
    "zoo_loss_doc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "zoo_loss_doc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Zooplankton Loss to DOC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "zoo_loss_doc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "zoo_loss_doc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Zooplankton Loss to DOC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "zoo_loss_poc_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "zoo_loss_poc_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Zooplankton Loss to POC Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "zoo_loss_poc_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "zoo_loss_poc_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Zooplankton Loss to POC Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "zoo_loss_zint_100m": {
        "standard_name": "air_temperature",
        "cesm_name": "zoo_loss_zint_100m",
        "units": "mmol/m^3 cm/s",
        "description": "Zooplankton Loss Vertical Integral 0-100m",
        "domain": "atmosphere",
        "component": "std"
    },
    "zoo_loss_zint": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "zoo_loss_zint",
        "units": "mmol/m^3 cm/s",
        "description": "Zooplankton Loss Vertical Integral",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_ALT_CO2_FLUX_IN": {
        "standard_name": "air_temperature",
        "cesm_name": "CaCO3_ALT_CO2_FLUX_IN",
        "units": "mmol/m^3 cm/s",
        "description": "CaCO3 Flux into Cell Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_ALT_CO2_REMIN": {
        "standard_name": "air_temperature",
        "cesm_name": "CaCO3_ALT_CO2_REMIN",
        "units": "mmol/m^3/s",
        "description": "CaCO3 Remineralization Alternative CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_FLUX_IN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CaCO3_FLUX_IN",
        "units": "mmol/m^3 cm/s",
        "description": "CaCO3 Flux into Cell",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_form": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CaCO3_form",
        "units": "mmol/m^3/s",
        "description": "Total CaCO3 Formation",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_PROD": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CaCO3_PROD",
        "units": "mmol/m^3/s",
        "description": "CaCO3 Production",
        "domain": "atmosphere",
        "component": "std"
    },
    "CaCO3_REMIN": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "CaCO3_REMIN",
        "units": "mmol/m^3/s",
        "description": "CaCO3 Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIA_IMPVF_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "DIA_IMPVF_DIC_ALT_CO2",
        "units": "mmol/m^3 cm/s",
        "description": "DIC_ALT_CO2 Flux Across Bottom Face from Diabatic Implicit Vertical Mixing",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIA_IMPVF_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIA_IMPVF_DIC",
        "units": "mmol/m^3 cm/s",
        "description": "DIC Flux Across Bottom Face from Diabatic Implicit Vertical Mixing",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIA_IMPVF_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DIA_IMPVF_DOCr",
        "units": "mmol/m^3 cm/s",
        "description": "DOCr Flux Across Bottom Face from Diabatic Implicit Vertical Mixing",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOC_remin": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOC_remin",
        "units": "mmol/m^3/s",
        "description": "DOC Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "DOCr_remin": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DOCr_remin",
        "units": "mmol/m^3/s",
        "description": "DOCr Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "DON_remin": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DON_remin",
        "units": "mmol/m^3/s",
        "description": "DON Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "DONr_remin": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "DONr_remin",
        "units": "mmol/m^3/s",
        "description": "DONr Remineralization",
        "domain": "atmosphere",
        "component": "std"
    },
    "graze_auto_TOT": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "graze_auto_TOT",
        "units": "mmol/m^3/s",
        "description": "Total Autotroph Grazing",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFB_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "HDIFB_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "DIC_ALT_CO2 Horizontal Diffusive Flux across Bottom Face",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFB_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFB_DIC",
        "units": "mmol/m^3/s",
        "description": "DIC Horizontal Diffusive Flux across Bottom Face",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFB_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFB_DOCr",
        "units": "mmol/m^3/s",
        "description": "DOCr Horizontal Diffusive Flux across Bottom Face",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFE_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFE_DOCr",
        "units": "mmol/m^3/s",
        "description": "DOCr Horizontal Diffusive Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "HDIFN_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "HDIFN_DOCr",
        "units": "mmol/m^3/s",
        "description": "DOCr Horizontal Diffusive Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "J_ALK_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "J_ALK_ALT_CO2",
        "units": "meq/m^3/s",
        "description": "Alkalinity Alternative CO2 Source Sink Term",
        "domain": "atmosphere",
        "component": "std"
    },
    "J_NO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "J_NO3",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Nitrate Source Sink Term",
        "domain": "atmosphere",
        "component": "std"
    },
    "J_SiO3": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "J_SiO3",
        "units": "mmol/m^3/s",
        "description": "Dissolved Inorganic Silicate Source Sink Term",
        "domain": "atmosphere",
        "component": "std"
    },
    "KPP_SRC_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "KPP_SRC_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "DIC_ALT_CO2 tendency from KPP non local mixing term",
        "domain": "atmosphere",
        "component": "std"
    },
    "KPP_SRC_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "KPP_SRC_DIC",
        "units": "mmol/m^3/s",
        "description": "DIC tendency from KPP non local mixing term",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_REMIN_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_REMIN_DIC",
        "units": "mmol/m^3/s",
        "description": "POC Remineralization routed to DIC",
        "domain": "atmosphere",
        "component": "std"
    },
    "POC_REMIN_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "POC_REMIN_DOCr",
        "units": "mmol/m^3/s",
        "description": "POC Remineralization routed to DOCr",
        "domain": "atmosphere",
        "component": "std"
    },
    "PON_REMIN_DONr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PON_REMIN_DONr",
        "units": "mmol/m^3/s",
        "description": "PON Remineralization routed to DONr",
        "domain": "atmosphere",
        "component": "std"
    },
    "PON_REMIN_NH4": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "PON_REMIN_NH4",
        "units": "mmol/m^3/s",
        "description": "PON Remineralization routed to NH4",
        "domain": "atmosphere",
        "component": "std"
    },
    "RF_TEND_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "RF_TEND_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "Robert Filter Tendency for DIC_ALT_CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "RF_TEND_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RF_TEND_DIC",
        "units": "mmol/m^3/s",
        "description": "Robert Filter Tendency for DIC",
        "domain": "atmosphere",
        "component": "std"
    },
    "RF_TEND_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RF_TEND_DOCr",
        "units": "mmol/m^3/s",
        "description": "Robert Filter Tendency for DOCr",
        "domain": "atmosphere",
        "component": "std"
    },
    "RF_TEND_DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RF_TEND_DOC",
        "units": "mmol/m^3/s",
        "description": "Robert Filter Tendency for DOC",
        "domain": "atmosphere",
        "component": "std"
    },
    "RF_TEND_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RF_TEND_Fe",
        "units": "mmol/m^3/s",
        "description": "Robert Filter Tendency for Fe",
        "domain": "atmosphere",
        "component": "std"
    },
    "RF_TEND_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RF_TEND_O2",
        "units": "mmol/m^3/s",
        "description": "Robert Filter Tendency for O2",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEND_DIC_ALT_CO2": {
        "standard_name": "air_temperature",
        "cesm_name": "TEND_DIC_ALT_CO2",
        "units": "mmol/m^3/s",
        "description": "Tendency of Thickness Weighted DIC_ALT_CO2",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEND_DIC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TEND_DIC",
        "units": "mmol/m^3/s",
        "description": "Tendency of Thickness Weighted DIC",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEND_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TEND_DOCr",
        "units": "mmol/m^3/s",
        "description": "Tendency of Thickness Weighted DOCr",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEND_DOC": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TEND_DOC",
        "units": "mmol/m^3/s",
        "description": "Tendency of Thickness Weighted DOC",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEND_Fe": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TEND_Fe",
        "units": "mmol/m^3/s",
        "description": "Tendency of Thickness Weighted Fe",
        "domain": "atmosphere",
        "component": "std"
    },
    "TEND_O2": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TEND_O2",
        "units": "mmol/m^3/s",
        "description": "Tendency of Thickness Weighted O2",
        "domain": "atmosphere",
        "component": "std"
    },
    "UE_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "UE_DOCr",
        "units": "mmol/m^3/s",
        "description": "DOCr Flux in grid-x direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "VN_DOCr": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "VN_DOCr",
        "units": "mmol/m^3/s",
        "description": "DOCr Flux in grid-y direction",
        "domain": "atmosphere",
        "component": "std"
    },
    "WT_DOCr": {
        "standard_name": "air_temperature",
        "cesm_name": "WT_DOCr",
        "units": "mmol/m^3/s",
        "description": "DOCr Flux Across Top Face",
        "domain": "atmosphere",
        "component": "std"
    },
    "RIVER_DISCHARGE_OVER_LAND_LIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "RIVER_DISCHARGE_OVER_LAND_LIQ",
        "units": "m3/s",
        "description": "MOSART river basin flow: LIQ",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTAL_DISCHARGE_TO_OCEAN_LIQ": {
        "standard_name": "specific_humidity",
        "cesm_name": "TOTAL_DISCHARGE_TO_OCEAN_LIQ",
        "units": "m3/s",
        "description": "MOSART total discharge into ocean: LIQ",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIRECT_DISCHARGE_TO_OCEAN_ICE": {
        "standard_name": "air_temperature",
        "cesm_name": "DIRECT_DISCHARGE_TO_OCEAN_ICE",
        "units": "m3/s",
        "description": "MOSART direct discharge into ocean: ICE",
        "domain": "atmosphere",
        "component": "std"
    },
    "DIRECT_DISCHARGE_TO_OCEAN_LIQ": {
        "standard_name": "air_temperature",
        "cesm_name": "DIRECT_DISCHARGE_TO_OCEAN_LIQ",
        "units": "m3/s",
        "description": "MOSART direct discharge into ocean: LIQ",
        "domain": "atmosphere",
        "component": "std"
    },
    "RIVER_DISCHARGE_OVER_LAND_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "RIVER_DISCHARGE_OVER_LAND_ICE",
        "units": "m3/s",
        "description": "MOSART river basin flow: ICE",
        "domain": "atmosphere",
        "component": "std"
    },
    "TOTAL_DISCHARGE_TO_OCEAN_ICE": {
        "standard_name": "unknown_standard_name",
        "cesm_name": "TOTAL_DISCHARGE_TO_OCEAN_ICE",
        "units": "m3/s",
        "description": "MOSART total discharge into ocean: ICE",
        "domain": "atmosphere",
        "component": "std"
    }
}

# Variable keyword mappings for detection
VARIABLE_KEYWORDS = {
    "CLDICE": [
        "ice",
        "averaged",
        "cloud",
        "cldice",
        "box",
        "grid"
    ],
    "CLDLIQ": [
        "averaged",
        "cloud",
        "box",
        "liquid",
        "grid",
        "cldliq"
    ],
    "CLOUD": [
        "fraction",
        "cloud"
    ],
    "CMFMCDZM": [
        "mass",
        "from",
        "deep",
        "convection",
        "flux",
        "cmfmcdzm"
    ],
    "CMFMC": [
        "mass",
        "convection",
        "deep",
        "cmfmc",
        "shallow",
        "moist"
    ],
    "DCQ": [
        "tendency",
        "processes",
        "dcq",
        "due",
        "moist"
    ],
    "DTCOND": [
        "dtcond",
        "tendency",
        "processes",
        "moist"
    ],
    "DTV": [
        "vertical",
        "diffusion",
        "dtv"
    ],
    "FSNTOA": [
        "net",
        "top",
        "solar",
        "atmosphere",
        "fsntoa",
        "flux"
    ],
    "MASS": [
        "grid",
        "box",
        "mass"
    ],
    "OMEGA": [
        "vertical",
        "omega",
        "velocity",
        "pressure"
    ],
    "PDELDRY": [
        "dry",
        "between",
        "difference",
        "pressure",
        "levels",
        "pdeldry"
    ],
    "QRL": [
        "longwave",
        "rate",
        "heating",
        "qrl"
    ],
    "QRS": [
        "rate",
        "heating",
        "solar",
        "qrs"
    ],
    "QSNOW": [
        "qsnow",
        "diagnostic",
        "snow",
        "mixing",
        "grid",
        "mean"
    ],
    "Q": [
        "static",
        "rho",
        "stability"
    ],
    "RELHUM": [
        "relative",
        "humidity",
        "relhum"
    ],
    "THzm": [
        "temp",
        "thzm",
        "zonal",
        "potential",
        "defined",
        "mean"
    ],
    "T": [
        "temperature"
    ],
    "U": [
        "zonal",
        "velocity",
        "wind"
    ],
    "UTGWORO": [
        "tendency",
        "drag",
        "wave",
        "orographic",
        "gravity",
        "utgworo"
    ],
    "UVzm": [
        "meridional",
        "uvzm",
        "zonal",
        "momentum",
        "zon",
        "flux"
    ],
    "UWzm": [
        "vertical",
        "uwzm",
        "zonal",
        "momentum",
        "zon",
        "flux"
    ],
    "Uzm": [
        "uzm",
        "zonal",
        "wind",
        "defined",
        "mean"
    ],
    "V": [
        "meridional",
        "velocity",
        "wind"
    ],
    "VTHzm": [
        "heat",
        "meridional",
        "vthzm",
        "zon",
        "flux",
        "mean"
    ],
    "Vzm": [
        "meridional",
        "zonal",
        "wind",
        "defined",
        "vzm",
        "mean"
    ],
    "Wzm": [
        "vertical",
        "zonal",
        "wind",
        "wzm",
        "defined",
        "mean"
    ],
    "Z3": [
        "above",
        "geopotential",
        "level",
        "sea",
        "height"
    ],
    "PRECT": [
        "precipitation",
        "prect",
        "rainfall",
        "convective",
        "total",
        "large",
        "scale",
        "and",
        "rain"
    ],
    "CLDLOW": [
        "cldlow",
        "vertically",
        "cloud",
        "low",
        "integrated"
    ],
    "CLDTOT": [
        "cldtot",
        "total",
        "vertically",
        "cloud",
        "integrated"
    ],
    "FLUT": [
        "top",
        "upwelling",
        "longwave",
        "flut",
        "model",
        "flux"
    ],
    "LHFLX": [
        "lhflx",
        "latent",
        "heat",
        "flux",
        "surface"
    ],
    "PRECC": [
        "precipitation",
        "ice",
        "rainfall",
        "convective",
        "liq",
        "precc",
        "rate",
        "rain"
    ],
    "PRECL": [
        "precipitation",
        "rainfall",
        "stable",
        "large",
        "scale",
        "rate",
        "precl",
        "rain"
    ],
    "UBOT": [
        "ubot",
        "lowest",
        "model",
        "zonal",
        "level",
        "wind"
    ],
    "VBOT": [
        "lowest",
        "meridional",
        "vbot",
        "model",
        "level",
        "wind"
    ],
    "IVT": [
        "vapor",
        "transport",
        "ivt",
        "integrated"
    ],
    "PS": [
        "surface",
        "pressure"
    ],
    "QREFHT": [
        "humidity",
        "qrefht",
        "reference",
        "height"
    ],
    "TMQ": [
        "water",
        "tmq",
        "vertically",
        "total",
        "precipitable",
        "integrated"
    ],
    "TS": [
        "surface",
        "temperature",
        "radiative"
    ],
    "uIVT": [
        "uivt",
        "unknown"
    ],
    "vIVT": [
        "vivt",
        "unknown"
    ],
    "bc_a1DDF": [
        "grav",
        "bc_a1ddf",
        "deposition",
        "dry",
        "bc a1ddf",
        "flux",
        "bottom"
    ],
    "bc_a1SFWET": [
        "bc_a1sfwet",
        "deposition",
        "wet",
        "bc a1sfwet",
        "flux",
        "surface"
    ],
    "bc_c1DDF": [
        "bc_c1ddf",
        "grav",
        "deposition",
        "bc c1ddf",
        "dry",
        "flux",
        "bottom"
    ],
    "bc_c1SFWET": [
        "surface",
        "deposition",
        "wet",
        "bc c1sfwet",
        "flux",
        "bc_c1sfwet"
    ],
    "bc_c1": [
        "water",
        "cloud",
        "bc c1",
        "bc_c1"
    ],
    "CFAD_DBZE94_CS": [
        "factor",
        "cfad",
        "ghz",
        "cfad_dbze94_cs",
        "cfad dbze94 cs",
        "radar",
        "reflectivity"
    ],
    "CFAD_SR532_CAL": [
        "lidar",
        "cfad",
        "ratio",
        "cfad sr532 cal",
        "scattering",
        "cfad_sr532_cal"
    ],
    "CLD_CAL_ICE": [
        "ice",
        "lidar",
        "cld_cal_ice",
        "cloud",
        "fraction",
        "cld cal ice"
    ],
    "CLD_CAL_LIQ": [
        "lidar",
        "cld_cal_liq",
        "cld cal liq",
        "cloud",
        "liquid",
        "fraction"
    ],
    "CLD_CAL_NOTCS": [
        "occurrence",
        "cld_cal_notcs",
        "but",
        "calipso",
        "cloud",
        "seen",
        "cld cal notcs"
    ],
    "CLD_CAL": [
        "cld cal",
        "lidar",
        "cld_cal",
        "cloud",
        "fraction"
    ],
    "CLD_CAL_UN": [
        "lidar",
        "cloud",
        "cld cal un",
        "fraction",
        "cld_cal_un",
        "phase",
        "undefined"
    ],
    "CLDHGH_CAL_ICE": [
        "ice",
        "high",
        "lidar",
        "cldhgh_cal_ice",
        "cldhgh cal ice",
        "level",
        "cloud"
    ],
    "CLDHGH_CAL_LIQ": [
        "cldhgh_cal_liq",
        "high",
        "lidar",
        "cldhgh cal liq",
        "cloud",
        "level",
        "liquid"
    ],
    "CLDHGH_CAL": [
        "cldhgh cal",
        "high",
        "lidar",
        "cldhgh_cal",
        "cloud",
        "level",
        "fraction"
    ],
    "CLDHGH_CAL_UN": [
        "high",
        "lidar",
        "cldhgh_cal_un",
        "level",
        "cldhgh cal un",
        "phase",
        "undefined"
    ],
    "CLDLOW_CAL_ICE": [
        "ice",
        "cldlow_cal_ice",
        "lidar",
        "low",
        "level",
        "cloud",
        "cldlow cal ice"
    ],
    "CLDLOW_CAL_LIQ": [
        "cldlow cal liq",
        "lidar",
        "low",
        "level",
        "cloud",
        "liquid",
        "cldlow_cal_liq"
    ],
    "CLDLOW_CAL": [
        "cldlow cal",
        "lidar",
        "cldlow_cal",
        "low",
        "level",
        "cloud",
        "fraction"
    ],
    "CLDLOW_CAL_UN": [
        "lidar",
        "cldlow_cal_un",
        "low",
        "level",
        "cldlow cal un",
        "phase",
        "undefined"
    ],
    "CLDMED_CAL_ICE": [
        "ice",
        "lidar",
        "mid",
        "cloud",
        "level",
        "cldmed_cal_ice",
        "cldmed cal ice"
    ],
    "CLDMED_CAL_LIQ": [
        "cldmed cal liq",
        "lidar",
        "mid",
        "cloud",
        "level",
        "liquid",
        "cldmed_cal_liq"
    ],
    "CLDMED_CAL": [
        "cldmed_cal",
        "lidar",
        "mid",
        "cldmed cal",
        "cloud",
        "level",
        "fraction"
    ],
    "CLDMED_CAL_UN": [
        "lidar",
        "mid",
        "cldmed_cal_un",
        "cldmed cal un",
        "level",
        "phase",
        "undefined"
    ],
    "CLD_MISR": [
        "cld_misr",
        "from",
        "cld misr",
        "cloud",
        "misr",
        "fraction",
        "simulator"
    ],
    "CLDTOT_CALCS": [
        "lidar",
        "temp",
        "cldtot_calcs",
        "total",
        "cloud",
        "and",
        "radar",
        "temperature",
        "cldtot calcs",
        "thermal"
    ],
    "CLDTOT_CAL_ICE": [
        "ice",
        "lidar",
        "temp",
        "cldtot cal ice",
        "total",
        "cloud",
        "temperature",
        "fraction",
        "thermal",
        "cldtot_cal_ice"
    ],
    "CLDTOT_CAL_LIQ": [
        "lidar",
        "temp",
        "total",
        "cldtot_cal_liq",
        "cloud",
        "liquid",
        "temperature",
        "fraction",
        "cldtot cal liq",
        "thermal"
    ],
    "CLDTOT_CAL": [
        "lidar",
        "temp",
        "total",
        "cloud",
        "temperature",
        "cldtot cal",
        "fraction",
        "thermal",
        "cldtot_cal"
    ],
    "CLDTOT_CAL_UN": [
        "cldtot_cal_un",
        "lidar",
        "temp",
        "cldtot cal un",
        "total",
        "cloud",
        "temperature",
        "phase",
        "thermal",
        "undefined"
    ],
    "CLDTOT_CS2": [
        "temp",
        "cldtot cs2",
        "cldtot_cs2",
        "total",
        "cloud",
        "radar",
        "temperature",
        "thermal",
        "without",
        "amount"
    ],
    "CLDTOT_CS": [
        "temp",
        "amount",
        "cldtot_cs",
        "total",
        "cloud",
        "radar",
        "temperature",
        "thermal",
        "cldtot cs"
    ],
    "CLDTOT_ISCCP": [
        "cldtot_isccp",
        "temp",
        "total",
        "cloud",
        "calculated",
        "the",
        "temperature",
        "fraction",
        "cldtot isccp",
        "thermal"
    ],
    "CLHMODIS": [
        "high",
        "modis",
        "fraction",
        "cloud",
        "level",
        "clhmodis"
    ],
    "CLIMODIS": [
        "ice",
        "climodis",
        "modis",
        "cloud",
        "fraction"
    ],
    "CLLMODIS": [
        "cllmodis",
        "modis",
        "low",
        "level",
        "cloud",
        "fraction"
    ],
    "CLMMODIS": [
        "mid",
        "modis",
        "cloud",
        "level",
        "fraction",
        "clmmodis"
    ],
    "CLMODIS": [
        "modis",
        "cloud",
        "area",
        "clmodis",
        "fraction"
    ],
    "CLRIMODIS": [
        "clrimodis",
        "modis",
        "cloud",
        "area",
        "fraction"
    ],
    "CLRLMODIS": [
        "modis",
        "cloud",
        "area",
        "fraction",
        "clrlmodis"
    ],
    "CLTMODIS": [
        "modis",
        "total",
        "cloud",
        "cltmodis",
        "fraction"
    ],
    "CLWMODIS": [
        "modis",
        "clwmodis",
        "cloud",
        "liquid",
        "fraction"
    ],
    "CO2_FFF": [
        "co2 fff",
        "co2_fff"
    ],
    "CO2_LND": [
        "co2 lnd",
        "co2_lnd"
    ],
    "CO2_OCN": [
        "co2_ocn",
        "co2 ocn"
    ],
    "dst_a1DDF": [
        "temp",
        "grav",
        "dst_a1ddf",
        "deposition",
        "dry",
        "temperature",
        "thermal",
        "flux",
        "dst a1ddf",
        "bottom"
    ],
    "dst_a1SFWET": [
        "temp",
        "deposition",
        "dst_a1sfwet",
        "wet",
        "temperature",
        "flux",
        "surface",
        "dst a1sfwet",
        "thermal"
    ],
    "dst_a3DDF": [
        "dst a3ddf",
        "temp",
        "grav",
        "deposition",
        "dst_a3ddf",
        "dry",
        "temperature",
        "thermal",
        "flux",
        "bottom"
    ],
    "dst_a3SFWET": [
        "dst a3sfwet",
        "temp",
        "deposition",
        "wet",
        "temperature",
        "dst_a3sfwet",
        "flux",
        "surface",
        "thermal"
    ],
    "dst_c1DDF": [
        "temp",
        "grav",
        "deposition",
        "dst c1ddf",
        "dry",
        "temperature",
        "thermal",
        "flux",
        "dst_c1ddf",
        "bottom"
    ],
    "dst_c1SFWET": [
        "temp",
        "dst c1sfwet",
        "deposition",
        "wet",
        "temperature",
        "dst_c1sfwet",
        "flux",
        "surface",
        "thermal"
    ],
    "dst_c1": [
        "temp",
        "water",
        "cloud",
        "dst c1",
        "temperature",
        "thermal",
        "dst_c1"
    ],
    "dst_c3DDF": [
        "dst c3ddf",
        "temp",
        "grav",
        "deposition",
        "dry",
        "temperature",
        "thermal",
        "dst_c3ddf",
        "flux",
        "bottom"
    ],
    "dst_c3SFWET": [
        "temp",
        "deposition",
        "wet",
        "dst_c3sfwet",
        "dst c3sfwet",
        "temperature",
        "flux",
        "surface",
        "thermal"
    ],
    "dst_c3": [
        "dst_c3",
        "temp",
        "water",
        "dst c3",
        "cloud",
        "temperature",
        "thermal"
    ],
    "FISCCP1_COSP": [
        "fisccp1_cosp",
        "each",
        "fraction",
        "covered",
        "box",
        "fisccp1 cosp",
        "grid"
    ],
    "FREQI": [
        "fractional",
        "occurrence",
        "ice",
        "freqi"
    ],
    "FREQL": [
        "occurrence",
        "liquid",
        "fractional",
        "freql"
    ],
    "ICIMR": [
        "ice",
        "prognostic",
        "cloud",
        "ratio",
        "mixing",
        "icimr"
    ],
    "ICWMR": [
        "water",
        "prognostic",
        "icwmr",
        "cloud",
        "ratio",
        "mixing"
    ],
    "IWC": [
        "ice",
        "average",
        "water",
        "box",
        "iwc",
        "grid"
    ],
    "IWPMODIS": [
        "iwpmodis",
        "ice",
        "water",
        "modis",
        "path",
        "cloud"
    ],
    "LWPMODIS": [
        "water",
        "modis",
        "path",
        "cloud",
        "liquid",
        "lwpmodis"
    ],
    "MEANCLDALB_ISCCP": [
        "cloud",
        "albedo",
        "meancldalb_isccp",
        "meancldalb isccp",
        "mean",
        "times"
    ],
    "MEANPTOP_ISCCP": [
        "top",
        "meanptop_isccp",
        "meanptop isccp",
        "pressure",
        "cloud",
        "mean",
        "times"
    ],
    "MEANTAU_ISCCP": [
        "meantau isccp",
        "meantau_isccp",
        "optical",
        "mean",
        "times",
        "thickness"
    ],
    "MEANTBCLR_ISCCP": [
        "clear",
        "meantbclr_isccp",
        "meantbclr isccp",
        "sky",
        "infrared",
        "from",
        "mean"
    ],
    "MEANTB_ISCCP": [
        "infrared",
        "meantb isccp",
        "from",
        "meantb_isccp",
        "isccp",
        "mean",
        "simulator"
    ],
    "ncl_a1DDF": [
        "grav",
        "deposition",
        "dry",
        "flux",
        "ncl a1ddf",
        "ncl_a1ddf",
        "bottom"
    ],
    "ncl_a1SFWET": [
        "deposition",
        "ncl a1sfwet",
        "wet",
        "ncl_a1sfwet",
        "flux",
        "surface"
    ],
    "ncl_a2DDF": [
        "ncl a2ddf",
        "grav",
        "deposition",
        "dry",
        "ncl_a2ddf",
        "flux",
        "bottom"
    ],
    "ncl_a2SFWET": [
        "deposition",
        "wet",
        "ncl_a2sfwet",
        "flux",
        "surface",
        "ncl a2sfwet"
    ],
    "ncl_a3DDF": [
        "grav",
        "deposition",
        "dry",
        "flux",
        "ncl a3ddf",
        "ncl_a3ddf",
        "bottom"
    ],
    "ncl_a3SFWET": [
        "deposition",
        "ncl_a3sfwet",
        "wet",
        "flux",
        "surface",
        "ncl a3sfwet"
    ],
    "ncl_c1DDF": [
        "grav",
        "deposition",
        "dry",
        "ncl_c1ddf",
        "ncl c1ddf",
        "flux",
        "bottom"
    ],
    "ncl_c1SFWET": [
        "ncl c1sfwet",
        "deposition",
        "wet",
        "ncl_c1sfwet",
        "flux",
        "surface"
    ],
    "ncl_c1": [
        "water",
        "ncl_c1",
        "cloud",
        "ncl c1"
    ],
    "ncl_c2DDF": [
        "grav",
        "deposition",
        "ncl_c2ddf",
        "dry",
        "ncl c2ddf",
        "flux",
        "bottom"
    ],
    "ncl_c2SFWET": [
        "ncl c2sfwet",
        "deposition",
        "wet",
        "ncl_c2sfwet",
        "flux",
        "surface"
    ],
    "ncl_c2": [
        "water",
        "ncl c2",
        "cloud",
        "ncl_c2"
    ],
    "ncl_c3DDF": [
        "grav",
        "ncl_c3ddf",
        "deposition",
        "dry",
        "ncl c3ddf",
        "flux",
        "bottom"
    ],
    "ncl_c3SFWET": [
        "deposition",
        "ncl c3sfwet",
        "wet",
        "ncl_c3sfwet",
        "flux",
        "surface"
    ],
    "ncl_c3": [
        "ncl c3",
        "cloud",
        "water",
        "ncl_c3"
    ],
    "num_a1DDF": [
        "num a1ddf",
        "grav",
        "deposition",
        "dry",
        "flux",
        "num_a1ddf",
        "bottom"
    ],
    "num_a1SFWET": [
        "num_a1sfwet",
        "num a1sfwet",
        "deposition",
        "wet",
        "flux",
        "surface"
    ],
    "num_a2DDF": [
        "grav",
        "deposition",
        "dry",
        "bottom",
        "flux",
        "num a2ddf",
        "num_a2ddf"
    ],
    "num_a2SFWET": [
        "deposition",
        "wet",
        "num a2sfwet",
        "num_a2sfwet",
        "flux",
        "surface"
    ],
    "num_a3DDF": [
        "grav",
        "deposition",
        "dry",
        "num a3ddf",
        "num_a3ddf",
        "flux",
        "bottom"
    ],
    "num_a3SFWET": [
        "num a3sfwet",
        "deposition",
        "num_a3sfwet",
        "wet",
        "flux",
        "surface"
    ],
    "num_c1DDF": [
        "grav",
        "deposition",
        "dry",
        "num_c1ddf",
        "flux",
        "bottom",
        "num c1ddf"
    ],
    "num_c1SFWET": [
        "num_c1sfwet",
        "deposition",
        "wet",
        "num c1sfwet",
        "flux",
        "surface"
    ],
    "num_c1": [
        "cloud",
        "num c1",
        "num_c1",
        "water"
    ],
    "num_c2DDF": [
        "grav",
        "deposition",
        "dry",
        "num_c2ddf",
        "bottom",
        "flux",
        "num c2ddf"
    ],
    "num_c2SFWET": [
        "deposition",
        "num_c2sfwet",
        "wet",
        "flux",
        "surface",
        "num c2sfwet"
    ],
    "num_c2": [
        "water",
        "cloud",
        "num_c2",
        "num c2"
    ],
    "num_c3DDF": [
        "grav",
        "deposition",
        "num c3ddf",
        "dry",
        "num_c3ddf",
        "flux",
        "bottom"
    ],
    "num_c3SFWET": [
        "deposition",
        "wet",
        "num c3sfwet",
        "num_c3sfwet",
        "flux",
        "surface"
    ],
    "num_c3": [
        "water",
        "cloud",
        "num_c3",
        "num c3"
    ],
    "NUMLIQ": [
        "numliq",
        "averaged",
        "cloud",
        "box",
        "liquid",
        "grid"
    ],
    "PCTMODIS": [
        "top",
        "modis",
        "pctmodis",
        "pressure",
        "cloud",
        "times"
    ],
    "pom_a1DDF": [
        "pom a1ddf",
        "grav",
        "deposition",
        "pom_a1ddf",
        "dry",
        "flux",
        "bottom"
    ],
    "pom_a1SFWET": [
        "deposition",
        "pom_a1sfwet",
        "wet",
        "pom a1sfwet",
        "flux",
        "surface"
    ],
    "pom_c1DDF": [
        "pom c1ddf",
        "grav",
        "deposition",
        "dry",
        "flux",
        "pom_c1ddf",
        "bottom"
    ],
    "pom_c1SFWET": [
        "deposition",
        "wet",
        "pom_c1sfwet",
        "pom c1sfwet",
        "flux",
        "surface"
    ],
    "pom_c1": [
        "pom c1",
        "cloud",
        "pom_c1",
        "water"
    ],
    "REFFCLIMODIS": [
        "ice",
        "particle",
        "modis",
        "reffclimodis",
        "cloud",
        "size"
    ],
    "REFFCLWMODIS": [
        "particle",
        "modis",
        "cloud",
        "liquid",
        "size",
        "reffclwmodis"
    ],
    "RFL_PARASOL": [
        "reflectance",
        "parasol",
        "rfl_parasol",
        "directional",
        "mono",
        "rfl parasol",
        "like"
    ],
    "SFCO2_FFF": [
        "sfco2_fff",
        "flux",
        "sfco2 fff",
        "surface"
    ],
    "SFCO2": [
        "flux",
        "surface",
        "sfco2"
    ],
    "so4_a1DDF": [
        "so4_a1ddf",
        "grav",
        "deposition",
        "dry",
        "so4 a1ddf",
        "flux",
        "bottom"
    ],
    "so4_a1SFWET": [
        "deposition",
        "so4 a1sfwet",
        "wet",
        "so4_a1sfwet",
        "flux",
        "surface"
    ],
    "so4_a2DDF": [
        "grav",
        "so4 a2ddf",
        "deposition",
        "dry",
        "so4_a2ddf",
        "flux",
        "bottom"
    ],
    "so4_a2SFWET": [
        "so4 a2sfwet",
        "deposition",
        "wet",
        "flux",
        "surface",
        "so4_a2sfwet"
    ],
    "so4_a3DDF": [
        "so4_a3ddf",
        "grav",
        "deposition",
        "so4 a3ddf",
        "dry",
        "flux",
        "bottom"
    ],
    "so4_a3SFWET": [
        "so4_a3sfwet",
        "deposition",
        "so4 a3sfwet",
        "wet",
        "flux",
        "surface"
    ],
    "so4_c1DDF": [
        "grav",
        "so4 c1ddf",
        "deposition",
        "so4_c1ddf",
        "dry",
        "flux",
        "bottom"
    ],
    "so4_c1SFWET": [
        "so4_c1sfwet",
        "deposition",
        "wet",
        "so4 c1sfwet",
        "flux",
        "surface"
    ],
    "so4_c1": [
        "water",
        "cloud",
        "so4_c1",
        "so4 c1"
    ],
    "so4_c2DDF": [
        "so4_c2ddf",
        "grav",
        "deposition",
        "dry",
        "flux",
        "so4 c2ddf",
        "bottom"
    ],
    "so4_c2SFWET": [
        "deposition",
        "wet",
        "so4 c2sfwet",
        "so4_c2sfwet",
        "flux",
        "surface"
    ],
    "so4_c2": [
        "water",
        "cloud",
        "so4 c2",
        "so4_c2"
    ],
    "so4_c3DDF": [
        "so4 c3ddf",
        "grav",
        "deposition",
        "dry",
        "bottom",
        "flux",
        "so4_c3ddf"
    ],
    "so4_c3SFWET": [
        "so4 c3sfwet",
        "deposition",
        "wet",
        "so4_c3sfwet",
        "flux",
        "surface"
    ],
    "so4_c3": [
        "cloud",
        "so4_c3",
        "so4 c3",
        "water"
    ],
    "soa_a1DDF": [
        "soa_a1ddf",
        "grav",
        "deposition",
        "dry",
        "soa a1ddf",
        "flux",
        "bottom"
    ],
    "soa_a1SFWET": [
        "deposition",
        "soa a1sfwet",
        "wet",
        "soa_a1sfwet",
        "flux",
        "surface"
    ],
    "soa_a2DDF": [
        "grav",
        "deposition",
        "dry",
        "soa_a2ddf",
        "soa a2ddf",
        "flux",
        "bottom"
    ],
    "soa_a2SFWET": [
        "soa_a2sfwet",
        "deposition",
        "wet",
        "soa a2sfwet",
        "flux",
        "surface"
    ],
    "soa_c1SFWET": [
        "deposition",
        "soa_c1sfwet",
        "soa c1sfwet",
        "wet",
        "flux",
        "surface"
    ],
    "soa_c1": [
        "cloud",
        "soa c1",
        "soa_c1",
        "water"
    ],
    "soa_c2SFWET": [
        "soa c2sfwet",
        "deposition",
        "wet",
        "soa_c2sfwet",
        "flux",
        "surface"
    ],
    "soa_c2": [
        "water",
        "cloud",
        "soa_c2",
        "soa c2"
    ],
    "TAUILOGMODIS": [
        "ice",
        "modis",
        "tauilogmodis",
        "cloud",
        "optical",
        "thickness"
    ],
    "TAUIMODIS": [
        "ice",
        "modis",
        "cloud",
        "tauimodis",
        "optical",
        "thickness"
    ],
    "TAUTLOGMODIS": [
        "modis",
        "total",
        "cloud",
        "optical",
        "tautlogmodis",
        "thickness"
    ],
    "TAUTMODIS": [
        "tautmodis",
        "modis",
        "total",
        "cloud",
        "optical",
        "thickness"
    ],
    "TAUWLOGMODIS": [
        "modis",
        "cloud",
        "thickness",
        "liquid",
        "optical",
        "tauwlogmodis"
    ],
    "TAUWMODIS": [
        "modis",
        "cloud",
        "liquid",
        "optical",
        "tauwmodis",
        "thickness"
    ],
    "TMCO2_FFF": [
        "burden",
        "tmco2_fff",
        "tmco2 fff",
        "column"
    ],
    "TMCO2_LND": [
        "burden",
        "tmco2_lnd",
        "column",
        "tmco2 lnd"
    ],
    "TMCO2_OCN": [
        "burden",
        "column",
        "tmco2 ocn",
        "tmco2_ocn"
    ],
    "VD01": [
        "vertical",
        "diffusion",
        "vd01"
    ],
    "WSUB": [
        "sub",
        "velocity",
        "diagnostic",
        "vertical",
        "wsub",
        "grid"
    ],
    "ACTNI": [
        "ice",
        "top",
        "average",
        "number",
        "cloud",
        "actni"
    ],
    "ACTNL": [
        "top",
        "average",
        "actnl",
        "number",
        "cloud",
        "droplet"
    ],
    "ACTREI": [
        "ice",
        "top",
        "actrei",
        "average",
        "effective",
        "cloud"
    ],
    "ACTREL": [
        "top",
        "average",
        "effective",
        "actrel",
        "cloud",
        "droplet"
    ],
    "AODVIS": [
        "aerosol",
        "aodvis",
        "only",
        "depth",
        "day",
        "optical"
    ],
    "BURDENBCdn": [
        "aerosol",
        "carbon",
        "black",
        "day",
        "burden",
        "burdenbcdn"
    ],
    "BURDENDUSTdn": [
        "dust",
        "aerosol",
        "day",
        "burden",
        "burdendustdn",
        "night"
    ],
    "BURDENPOMdn": [
        "aerosol",
        "pom",
        "day",
        "burden",
        "night",
        "burdenpomdn"
    ],
    "BURDENSEASALTdn": [
        "aerosol",
        "seasalt",
        "day",
        "burden",
        "burdenseasaltdn",
        "night"
    ],
    "BURDENSO4dn": [
        "burdenso4dn",
        "aerosol",
        "sulfate",
        "day",
        "burden",
        "night"
    ],
    "BURDENSO4": [
        "aerosol",
        "only",
        "sulfate",
        "day",
        "burden",
        "burdenso4"
    ],
    "BURDENSOAdn": [
        "burdensoadn",
        "aerosol",
        "day",
        "burden",
        "night",
        "soa"
    ],
    "CDNUMC": [
        "concentration",
        "vertically",
        "cdnumc",
        "droplet",
        "integrated"
    ],
    "FCTI": [
        "occurrence",
        "top",
        "ice",
        "fractional",
        "fcti",
        "cloud"
    ],
    "FCTL": [
        "occurrence",
        "top",
        "fractional",
        "cloud",
        "liquid",
        "fctl"
    ],
    "FLDSC": [
        "downwelling",
        "longwave",
        "fldsc",
        "clearsky",
        "flux",
        "surface"
    ],
    "FLDS": [
        "columns",
        "downscaled",
        "flds",
        "atmospheric",
        "longwave",
        "radiation"
    ],
    "FLNR": [
        "net",
        "longwave",
        "tropopause",
        "flux",
        "flnr"
    ],
    "FLNSC": [
        "net",
        "longwave",
        "clearsky",
        "flnsc",
        "flux",
        "surface"
    ],
    "FLNS": [
        "net",
        "flns",
        "longwave",
        "flux",
        "surface"
    ],
    "FLNTC": [
        "net",
        "top",
        "flntc",
        "longwave",
        "clearsky",
        "flux"
    ],
    "FLNT": [
        "net",
        "top",
        "longwave",
        "model",
        "flux",
        "flnt"
    ],
    "FLUTC": [
        "top",
        "upwelling",
        "longwave",
        "clearsky",
        "flutc",
        "flux"
    ],
    "FSDSC": [
        "downwelling",
        "solar",
        "clearsky",
        "flux",
        "surface",
        "fsdsc"
    ],
    "FSDS": [
        "atmospheric",
        "radiation",
        "solar",
        "fsds",
        "incident"
    ],
    "FSNR": [
        "net",
        "solar",
        "tropopause",
        "flux",
        "fsnr"
    ],
    "FSNSC": [
        "net",
        "solar",
        "clearsky",
        "fsnsc",
        "flux",
        "surface"
    ],
    "FSNS": [
        "net",
        "fsns",
        "solar",
        "flux",
        "surface"
    ],
    "FSNTOAC": [
        "net",
        "top",
        "fsntoac",
        "solar",
        "clearsky",
        "flux"
    ],
    "FSNT": [
        "net",
        "top",
        "solar",
        "model",
        "fsnt",
        "flux"
    ],
    "LWCF": [
        "longwave",
        "forcing",
        "cloud",
        "lwcf"
    ],
    "MSKtem": [
        "tem",
        "mask",
        "msktem"
    ],
    "OMEGA500": [
        "velocity",
        "vertical",
        "mbar",
        "pressure",
        "surface",
        "omega500"
    ],
    "PBLH": [
        "height",
        "pbl",
        "pblh"
    ],
    "PHIS": [
        "phis",
        "geopotential",
        "surface"
    ],
    "PRECSC": [
        "precipitation",
        "rainfall",
        "water",
        "snow",
        "convective",
        "equivalent",
        "rate",
        "rain",
        "precsc"
    ],
    "PRECSL": [
        "precipitation",
        "rainfall",
        "snow",
        "stable",
        "large",
        "scale",
        "precsl",
        "rate",
        "rain"
    ],
    "PRECTMX": [
        "prectmx",
        "precipitation",
        "rainfall",
        "maximum",
        "convective",
        "large",
        "scale",
        "and",
        "rain"
    ],
    "PSL": [
        "level",
        "sea",
        "psl",
        "pressure"
    ],
    "Q200": [
        "specific",
        "mbar",
        "humidity",
        "q200",
        "pressure",
        "surface"
    ],
    "Q500": [
        "specific",
        "mbar",
        "q500",
        "humidity",
        "pressure",
        "surface"
    ],
    "Q700": [
        "q700",
        "velocity",
        "vertical",
        "mbar",
        "pressure",
        "surface"
    ],
    "Q850": [
        "specific",
        "mbar",
        "humidity",
        "pressure",
        "q850",
        "surface"
    ],
    "RHREFHT": [
        "relative",
        "rhrefht",
        "humidity",
        "reference",
        "height"
    ],
    "SHFLX": [
        "heat",
        "shflx",
        "sensible",
        "flux",
        "surface"
    ],
    "SOLIN": [
        "solar",
        "solin",
        "insolation"
    ],
    "SOLLD": [
        "infrared",
        "diffuse",
        "solar",
        "near",
        "downward",
        "solld"
    ],
    "SOLSD": [
        "diffuse",
        "solar",
        "visible",
        "solsd",
        "downward",
        "surface"
    ],
    "SWCF": [
        "forcing",
        "shortwave",
        "cloud",
        "swcf"
    ],
    "T010": [
        "t010",
        "mbar",
        "pressure",
        "temperature",
        "surface"
    ],
    "T200": [
        "mbar",
        "pressure",
        "temperature",
        "surface",
        "t200"
    ],
    "T500": [
        "mbar",
        "pressure",
        "temperature",
        "t500",
        "surface"
    ],
    "T700": [
        "mbar",
        "pressure",
        "t700",
        "temperature",
        "surface"
    ],
    "T850": [
        "mbar",
        "pressure",
        "temperature",
        "t850",
        "surface"
    ],
    "TAUBLJX": [
        "taubljx",
        "drag",
        "from",
        "beljaars",
        "zonal",
        "integrated"
    ],
    "TAUBLJY": [
        "drag",
        "meridional",
        "from",
        "taubljy",
        "beljaars",
        "integrated"
    ],
    "TAUGWX": [
        "surface",
        "stress",
        "wave",
        "zonal",
        "taugwx",
        "gravity"
    ],
    "TAUGWY": [
        "taugwy",
        "surface",
        "stress",
        "meridional",
        "wave",
        "gravity"
    ],
    "TAUX": [
        "direction",
        "grid",
        "taux",
        "windstress"
    ],
    "TAUY": [
        "direction",
        "grid",
        "windstress",
        "tauy"
    ],
    "TGCLDIWP": [
        "ice",
        "tgcldiwp",
        "total",
        "cloud",
        "box",
        "grid"
    ],
    "TGCLDLWP": [
        "total",
        "cloud",
        "box",
        "liquid",
        "grid",
        "tgcldlwp"
    ],
    "TREFHTMN": [
        "minimum",
        "trefhtmn",
        "reference",
        "temperature",
        "over",
        "height"
    ],
    "TREFHTMX": [
        "maximum",
        "reference",
        "trefhtmx",
        "temperature",
        "over",
        "height"
    ],
    "TREFHT": [
        "temperature",
        "trefht",
        "reference",
        "height"
    ],
    "TSMN": [
        "output",
        "minimum",
        "tsmn",
        "surface",
        "temperature",
        "over"
    ],
    "TSMX": [
        "output",
        "maximum",
        "tsmx",
        "over",
        "temperature",
        "surface"
    ],
    "U010": [
        "mbar",
        "pressure",
        "zonal",
        "u010",
        "wind",
        "surface"
    ],
    "U10": [
        "u10",
        "wind"
    ],
    "U200": [
        "u200",
        "mbar",
        "pressure",
        "zonal",
        "wind",
        "surface"
    ],
    "U500": [
        "u500",
        "mbar",
        "pressure",
        "zonal",
        "wind",
        "surface"
    ],
    "U700": [
        "mbar",
        "pressure",
        "zonal",
        "wind",
        "u700",
        "surface"
    ],
    "U850": [
        "mbar",
        "pressure",
        "zonal",
        "u850",
        "wind",
        "surface"
    ],
    "UV": [
        "flux",
        "momentum"
    ],
    "V010": [
        "meridional",
        "mbar",
        "pressure",
        "wind",
        "v010",
        "surface"
    ],
    "V200": [
        "meridional",
        "mbar",
        "pressure",
        "v200",
        "wind",
        "surface"
    ],
    "V500": [
        "v500",
        "meridional",
        "mbar",
        "pressure",
        "wind",
        "surface"
    ],
    "V700": [
        "v700",
        "meridional",
        "mbar",
        "pressure",
        "wind",
        "surface"
    ],
    "V850": [
        "v850",
        "meridional",
        "mbar",
        "pressure",
        "wind",
        "surface"
    ],
    "VQ": [
        "meridional",
        "transport",
        "water"
    ],
    "VT": [
        "meridional",
        "heat",
        "transport"
    ],
    "VZ": [
        "meridional",
        "geopotential",
        "transport",
        "energy"
    ],
    "WSPDSRFAV": [
        "horizontal",
        "average",
        "speed",
        "total",
        "wspdsrfav",
        "wind"
    ],
    "WSPDSRFMX": [
        "horizontal",
        "wspdsrfmx",
        "maximum",
        "speed",
        "total",
        "wind"
    ],
    "Z050": [
        "z050",
        "mbar",
        "pressure",
        "geopotential",
        "surface"
    ],
    "Z200": [
        "mbar",
        "pressure",
        "geopotential",
        "z200",
        "surface"
    ],
    "Z500": [
        "mbar",
        "pressure",
        "geopotential",
        "surface",
        "z500",
        "height"
    ],
    "Z700": [
        "z700",
        "mbar",
        "pressure",
        "geopotential",
        "surface"
    ],
    "Z850": [
        "mbar",
        "pressure",
        "geopotential",
        "z850",
        "surface"
    ],
    "Z300": [
        "mbar",
        "z300",
        "pressure",
        "geopotential",
        "surface",
        "height"
    ],
    "ABSORB": [
        "absorption",
        "aerosol",
        "only",
        "day",
        "absorb"
    ],
    "ac_CO2": [
        "emission",
        "ac_co2",
        "aircraft",
        "ac co2"
    ],
    "ADRAIN": [
        "precipitation",
        "rainfall",
        "average",
        "diameter",
        "effective",
        "adrain",
        "rain"
    ],
    "ADSNOW": [
        "average",
        "diameter",
        "adsnow",
        "effective",
        "snow"
    ],
    "AEROD_v": [
        "aerod v",
        "aerosol",
        "visible",
        "total",
        "depth",
        "optical",
        "aerod_v"
    ],
    "ANRAIN": [
        "precipitation",
        "anrain",
        "rainfall",
        "average",
        "number",
        "conc",
        "rain"
    ],
    "ANSNOW": [
        "average",
        "ansnow",
        "snow",
        "number",
        "conc"
    ],
    "AODABSdn": [
        "absorption",
        "aerosol",
        "depth",
        "day",
        "optical",
        "aodabsdn"
    ],
    "AODBCdn": [
        "aerosol",
        "aodbcdn",
        "from",
        "depth",
        "day",
        "optical"
    ],
    "AODdnDUST1": [
        "aerosol",
        "aoddndust1",
        "depth",
        "day",
        "night",
        "optical"
    ],
    "AODdnDUST2": [
        "aerosol",
        "aoddndust2",
        "depth",
        "day",
        "night",
        "optical"
    ],
    "AODdnDUST3": [
        "aerosol",
        "aoddndust3",
        "depth",
        "day",
        "night",
        "optical"
    ],
    "AODdnMODE1": [
        "aerosol",
        "depth",
        "day",
        "night",
        "optical",
        "aoddnmode1"
    ],
    "AODdnMODE2": [
        "aerosol",
        "aoddnmode2",
        "depth",
        "day",
        "night",
        "optical"
    ],
    "AODdnMODE3": [
        "aerosol",
        "depth",
        "day",
        "night",
        "optical",
        "aoddnmode3"
    ],
    "AODDUST1": [
        "aerosol",
        "aoddust1",
        "only",
        "depth",
        "day",
        "optical"
    ],
    "AODDUST2": [
        "aoddust2"
    ],
    "AODDUST3": [
        "aerosol",
        "only",
        "depth",
        "day",
        "optical",
        "aoddust3"
    ],
    "AODDUST": [
        "dust",
        "aerosol",
        "from",
        "aoddust",
        "depth",
        "optical"
    ],
    "AODNIRstdn": [
        "stratospheric",
        "aerosol",
        "aodnirstdn",
        "depth",
        "day",
        "optical"
    ],
    "AODPOMdn": [
        "aerosol",
        "aodpomdn",
        "from",
        "depth",
        "optical",
        "pom"
    ],
    "AODSO4dn": [
        "aerosol",
        "from",
        "aodso4dn",
        "depth",
        "day",
        "optical"
    ],
    "AODSOAdn": [
        "aerosol",
        "from",
        "depth",
        "optical",
        "aodsoadn",
        "soa"
    ],
    "AODSSdn": [
        "aerosol",
        "seasalt",
        "from",
        "aodssdn",
        "depth",
        "optical"
    ],
    "AODUVdn": [
        "aerosol",
        "aoduvdn",
        "depth",
        "day",
        "night",
        "optical"
    ],
    "AODUVstdn": [
        "aoduvstdn",
        "stratospheric",
        "aerosol",
        "depth",
        "day",
        "optical"
    ],
    "AODVISdn": [
        "aerosol",
        "depth",
        "day",
        "aodvisdn",
        "night",
        "optical"
    ],
    "AODVISstdn": [
        "stratospheric",
        "aerosol",
        "depth",
        "day",
        "aodvisstdn",
        "optical"
    ],
    "AQRAIN": [
        "precipitation",
        "rainfall",
        "average",
        "aqrain",
        "ratio",
        "mixing",
        "rain"
    ],
    "AQSNOW": [
        "average",
        "snow",
        "aqsnow",
        "ratio",
        "mixing"
    ],
    "AQ_SO2": [
        "aq so2",
        "chemistry",
        "aqueous",
        "for",
        "gas",
        "species",
        "aq_so2"
    ],
    "AREA": [
        "grid",
        "box",
        "area"
    ],
    "AREI": [
        "ice",
        "average",
        "effective",
        "arei",
        "radius"
    ],
    "AREL": [
        "average",
        "effective",
        "arel",
        "droplet",
        "radius"
    ],
    "AWNC": [
        "average",
        "water",
        "awnc",
        "number",
        "cloud",
        "conc"
    ],
    "AWNI": [
        "ice",
        "average",
        "awni",
        "number",
        "cloud",
        "conc"
    ],
    "bc_a1_SRF": [
        "layer",
        "bc a1 srf",
        "bc_a1_srf",
        "bottom"
    ],
    "bc_a1": [
        "concentration",
        "bc a1",
        "bc_a1"
    ],
    "bc_a4_CLXF": [
        "for",
        "bc a4 clxf",
        "vertically",
        "forcing",
        "intergrated",
        "bc_a4_clxf",
        "external"
    ],
    "bc_a4_CMXF": [
        "for",
        "vertically",
        "forcing",
        "bc_a4_cmxf",
        "intergrated",
        "external",
        "bc a4 cmxf"
    ],
    "bc_a4DDF": [
        "grav",
        "bc a4ddf",
        "deposition",
        "dry",
        "bc_a4ddf",
        "flux",
        "bottom"
    ],
    "bc_a4SFWET": [
        "bc_a4sfwet",
        "deposition",
        "wet",
        "bc a4sfwet",
        "flux",
        "surface"
    ],
    "bc_a4_SRF": [
        "bc_a4_srf",
        "bc a4 srf",
        "bottom",
        "layer"
    ],
    "bc_a4": [
        "bc_a4",
        "bc a4",
        "concentration"
    ],
    "bc_c4DDF": [
        "bc_c4ddf",
        "grav",
        "deposition",
        "bc c4ddf",
        "dry",
        "flux",
        "bottom"
    ],
    "bc_c4SFWET": [
        "bc_c4sfwet",
        "deposition",
        "wet",
        "bc c4sfwet",
        "flux",
        "surface"
    ],
    "bc_c4": [
        "water",
        "bc c4",
        "cloud",
        "bc_c4"
    ],
    "BROX": [
        "brox",
        "bro",
        "brcl",
        "hobr"
    ],
    "BROY": [
        "inorganic",
        "bro",
        "hobr",
        "total",
        "bromine",
        "broy"
    ],
    "CAPE": [
        "cape",
        "available",
        "convectively",
        "potential",
        "energy"
    ],
    "CCN3": [
        "concentration",
        "ccn3",
        "ccn"
    ],
    "CLDHGH": [
        "high",
        "vertically",
        "cloud",
        "cldhgh",
        "integrated"
    ],
    "CLDMED": [
        "mid",
        "cldmed",
        "vertically",
        "cloud",
        "level",
        "integrated"
    ],
    "CLOUDCOVER_CLUBB": [
        "cover",
        "cloud",
        "cloudcover clubb",
        "cloudcover_clubb"
    ],
    "CLOUDFRAC_CLUBB": [
        "cloud",
        "fraction",
        "cloudfrac_clubb",
        "cloudfrac clubb"
    ],
    "CLOX": [
        "oclo",
        "clo",
        "hocl",
        "clox"
    ],
    "CLOY": [
        "cloy",
        "clo",
        "chlorine",
        "oclo",
        "inorganic",
        "total"
    ],
    "CME": [
        "cme",
        "evap",
        "within",
        "the",
        "rate",
        "cond"
    ],
    "CMFDQ": [
        "cmfdq",
        "shallow",
        "tendency",
        "convection"
    ],
    "CO2": [
        "co2"
    ],
    "CONCLD": [
        "cloud",
        "convective",
        "concld",
        "cover"
    ],
    "DF_H2O2": [
        "df h2o2",
        "deposition",
        "dry",
        "flux",
        "df_h2o2"
    ],
    "DF_H2SO4": [
        "df_h2so4",
        "deposition",
        "df h2so4",
        "dry",
        "flux"
    ],
    "DF_SO2": [
        "df so2",
        "deposition",
        "dry",
        "flux",
        "df_so2"
    ],
    "dgnumwet1": [
        "aerosol",
        "diameter",
        "wet",
        "mode",
        "dgnumwet1"
    ],
    "dgnumwet2": [
        "aerosol",
        "diameter",
        "wet",
        "mode",
        "dgnumwet2"
    ],
    "dgnumwet3": [
        "aerosol",
        "diameter",
        "wet",
        "mode",
        "dgnumwet3"
    ],
    "DH2O2CHM": [
        "net",
        "tendency",
        "dh2o2chm",
        "chem",
        "from"
    ],
    "DMS_SRF": [
        "dms",
        "layer",
        "dms srf",
        "dms_srf",
        "bottom"
    ],
    "DMS": [
        "dms",
        "concentration"
    ],
    "dry_deposition_NHx_as_N": [
        "dry deposition nhx as n",
        "nhx",
        "dry_deposition_nhx_as_n",
        "deposition",
        "dry",
        "flux"
    ],
    "dry_deposition_NOy_as_N": [
        "dry_deposition_noy_as_n",
        "noy",
        "dry deposition noy as n",
        "deposition",
        "dry",
        "flux"
    ],
    "Dso4_a1CHM": [
        "net",
        "tendency",
        "chem",
        "from",
        "dso4 a1chm",
        "dso4_a1chm"
    ],
    "Dso4_a2CHM": [
        "net",
        "tendency",
        "chem",
        "from",
        "dso4 a2chm",
        "dso4_a2chm"
    ],
    "Dso4_a3CHM": [
        "net",
        "tendency",
        "chem",
        "from",
        "dso4 a3chm",
        "dso4_a3chm"
    ],
    "dst_a1SF": [
        "dst_a1sf",
        "dust",
        "dst a1sf",
        "temp",
        "emission",
        "temperature",
        "surface",
        "thermal"
    ],
    "dst_a1_SRF": [
        "layer",
        "temp",
        "dst a1 srf",
        "temperature",
        "thermal",
        "bottom",
        "dst_a1_srf"
    ],
    "dst_a1": [
        "concentration",
        "temp",
        "dst_a1",
        "temperature",
        "dst a1",
        "thermal"
    ],
    "dst_a2DDF": [
        "temp",
        "grav",
        "dst_a2ddf",
        "deposition",
        "dry",
        "dst a2ddf",
        "temperature",
        "thermal",
        "flux",
        "bottom"
    ],
    "dst_a2SF": [
        "dust",
        "temp",
        "emission",
        "dst_a2sf",
        "dst a2sf",
        "temperature",
        "surface",
        "thermal"
    ],
    "dst_a2SFWET": [
        "dst a2sfwet",
        "dst_a2sfwet",
        "temp",
        "deposition",
        "wet",
        "temperature",
        "flux",
        "surface",
        "thermal"
    ],
    "dst_a2_SRF": [
        "layer",
        "dst_a2_srf",
        "temp",
        "dst a2 srf",
        "temperature",
        "thermal",
        "bottom"
    ],
    "dst_a2": [
        "concentration",
        "temp",
        "dst a2",
        "temperature",
        "dst_a2",
        "thermal"
    ],
    "dst_a3SF": [
        "dust",
        "temp",
        "dst_a3sf",
        "emission",
        "temperature",
        "thermal",
        "surface",
        "dst a3sf"
    ],
    "dst_a3_SRF": [
        "layer",
        "temp",
        "dst a3 srf",
        "temperature",
        "thermal",
        "dst_a3_srf",
        "bottom"
    ],
    "dst_a3": [
        "concentration",
        "temp",
        "dst_a3",
        "temperature",
        "dst a3",
        "thermal"
    ],
    "dst_c2DDF": [
        "dst_c2ddf",
        "temp",
        "grav",
        "deposition",
        "dry",
        "dst c2ddf",
        "temperature",
        "thermal",
        "flux",
        "bottom"
    ],
    "dst_c2SFWET": [
        "temp",
        "deposition",
        "wet",
        "dst_c2sfwet",
        "dst c2sfwet",
        "temperature",
        "flux",
        "surface",
        "thermal"
    ],
    "dst_c2": [
        "dst c2",
        "temp",
        "water",
        "cloud",
        "temperature",
        "thermal",
        "dst_c2"
    ],
    "DTCORE": [
        "tendency",
        "core",
        "dynamical",
        "dtcore",
        "due"
    ],
    "DTWR_H2O2": [
        "neu",
        "tendency",
        "dtwr_h2o2",
        "scheme",
        "removal",
        "wet",
        "dtwr h2o2"
    ],
    "DTWR_H2SO4": [
        "neu",
        "tendency",
        "scheme",
        "removal",
        "wet",
        "dtwr_h2so4",
        "dtwr h2so4"
    ],
    "DTWR_SO2": [
        "neu",
        "tendency",
        "dtwr_so2",
        "scheme",
        "removal",
        "wet",
        "dtwr so2"
    ],
    "EVAPPREC": [
        "precipitation",
        "rainfall",
        "evapprec",
        "precip",
        "rate",
        "falling",
        "evaporation",
        "rain"
    ],
    "EVAPQZM": [
        "tendency",
        "from",
        "evapqzm",
        "zhang",
        "evaporation",
        "mcfarlane"
    ],
    "EVAPTZM": [
        "tendency",
        "from",
        "snow",
        "evaptzm",
        "evaporation",
        "prod"
    ],
    "EXTINCTdn": [
        "aerosol",
        "day",
        "extinctdn",
        "night",
        "extinction"
    ],
    "EXTINCTNIRdn": [
        "aerosol",
        "extinctnirdn",
        "day",
        "night",
        "extinction"
    ],
    "EXTINCTUVdn": [
        "aerosol",
        "day",
        "night",
        "extinctuvdn",
        "extinction"
    ],
    "EXTxASYMdn": [
        "factor",
        "asymmetry",
        "extxasymdn",
        "day",
        "times",
        "extinction"
    ],
    "FICE": [
        "fice",
        "ice",
        "content",
        "within",
        "fractional",
        "cloud"
    ],
    "FLNTCLR": [
        "flntclr",
        "points",
        "net",
        "only",
        "longwave",
        "clearsky"
    ],
    "FREQCLR": [
        "occurrence",
        "freqclr",
        "frequency",
        "clearsky"
    ],
    "FREQR": [
        "occurrence",
        "freqr",
        "fractional",
        "rain"
    ],
    "FREQS": [
        "occurrence",
        "freqs",
        "snow",
        "fractional"
    ],
    "FREQZM": [
        "fractional",
        "convection",
        "occurance",
        "freqzm"
    ],
    "FSNTC": [
        "net",
        "top",
        "fsntc",
        "solar",
        "clearsky",
        "flux"
    ],
    "FSUTOA": [
        "top",
        "upwelling",
        "solar",
        "atmosphere",
        "flux",
        "fsutoa"
    ],
    "GS_SO2": [
        "gs_so2",
        "chemistry",
        "gs so2",
        "removal",
        "wet",
        "for",
        "gas"
    ],
    "H2O2_SRF": [
        "layer",
        "h2o2 srf",
        "h2o2_srf",
        "bottom"
    ],
    "H2O2": [
        "concentration",
        "h2o2"
    ],
    "H2O_CLXF": [
        "h2o_clxf",
        "for",
        "vertically",
        "forcing",
        "h2o clxf",
        "intergrated",
        "external"
    ],
    "H2O_CMXF": [
        "h2o cmxf",
        "h2o_cmxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "external"
    ],
    "H2O_SRF": [
        "layer",
        "h2o srf",
        "water",
        "h2o_srf",
        "vapor",
        "bottom"
    ],
    "H2O": [
        "water",
        "h2o",
        "vapor",
        "concentration"
    ],
    "H2SO4M_C": [
        "aerosol",
        "mass",
        "h2so4m_c",
        "sulfate",
        "h2so4m c",
        "chemical"
    ],
    "H2SO4_sfnnuc1": [
        "new",
        "tendency",
        "h2so4 sfnnuc1",
        "nucleation",
        "particle",
        "h2so4_sfnnuc1",
        "column"
    ],
    "H2SO4_SRF": [
        "layer",
        "h2so4_srf",
        "h2so4 srf",
        "bottom"
    ],
    "H2SO4": [
        "concentration",
        "h2so4"
    ],
    "HCL_GAS": [
        "hcl",
        "hcl gas",
        "gas",
        "hcl_gas",
        "phase"
    ],
    "HNO3_GAS": [
        "gas",
        "hno3 gas",
        "phase",
        "hno3_gas"
    ],
    "HNO3_NAT": [
        "condensed",
        "hno3 nat",
        "nat",
        "hno3_nat"
    ],
    "HNO3_STS": [
        "hno3 sts",
        "sts",
        "hno3_sts",
        "condensed"
    ],
    "HO2": [
        "ho2",
        "prescribed",
        "tracer",
        "constituent"
    ],
    "ICEFRAC": [
        "icefrac",
        "covered",
        "area",
        "sea",
        "fraction",
        "sfc"
    ],
    "jh2o2": [
        "rate",
        "jh2o2",
        "photolysis",
        "constant"
    ],
    "KVH_CLUBB": [
        "moisture",
        "heat",
        "diffusivity",
        "kvh_clubb",
        "kvh clubb",
        "vertical",
        "clubb"
    ],
    "LANDFRAC": [
        "landfrac",
        "covered",
        "area",
        "fraction",
        "sfc",
        "land"
    ],
    "ncl_a1SF": [
        "seasalt",
        "emission",
        "ncl_a1sf",
        "ncl a1sf",
        "surface"
    ],
    "ncl_a1_SRF": [
        "layer",
        "ncl_a1_srf",
        "ncl a1 srf",
        "bottom"
    ],
    "ncl_a1": [
        "ncl_a1",
        "concentration",
        "ncl a1"
    ],
    "ncl_a2SF": [
        "seasalt",
        "ncl a2sf",
        "emission",
        "ncl_a2sf",
        "surface"
    ],
    "ncl_a2_SRF": [
        "ncl_a2_srf",
        "ncl a2 srf",
        "bottom",
        "layer"
    ],
    "ncl_a2": [
        "concentration",
        "ncl_a2",
        "ncl a2"
    ],
    "ncl_a3SF": [
        "seasalt",
        "emission",
        "ncl a3sf",
        "ncl_a3sf",
        "surface"
    ],
    "ncl_a3_SRF": [
        "layer",
        "bottom",
        "ncl_a3_srf",
        "ncl a3 srf"
    ],
    "ncl_a3": [
        "ncl a3",
        "concentration",
        "ncl_a3"
    ],
    "NITROP_PD": [
        "nitrop pd",
        "tropopause",
        "nitrop_pd",
        "probability",
        "chemical"
    ],
    "NO3": [
        "no3",
        "nitrate",
        "inorganic",
        "dissolved"
    ],
    "NOX": [
        "nox"
    ],
    "NOY": [
        "total",
        "nitrogen",
        "noy",
        "orgnoy"
    ],
    "num_a1_CLXF": [
        "num a1 clxf",
        "num_a1_clxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "external"
    ],
    "num_a1_CMXF": [
        "num_a1_cmxf",
        "num a1 cmxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "external"
    ],
    "num_a1SF": [
        "dust",
        "emission",
        "num_a1sf",
        "surface",
        "num a1sf"
    ],
    "num_a1_SRF": [
        "layer",
        "num a1 srf",
        "num_a1_srf",
        "bottom"
    ],
    "num_a1": [
        "num a1",
        "concentration",
        "num_a1"
    ],
    "num_a2_CLXF": [
        "num_a2_clxf",
        "for",
        "num a2 clxf",
        "vertically",
        "forcing",
        "intergrated",
        "external"
    ],
    "num_a2_CMXF": [
        "num_a2_cmxf",
        "num a2 cmxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "external"
    ],
    "num_a2_sfnnuc1": [
        "new",
        "tendency",
        "nucleation",
        "particle",
        "num_a2_sfnnuc1",
        "num a2 sfnnuc1",
        "column"
    ],
    "num_a2SF": [
        "dust",
        "num_a2sf",
        "emission",
        "surface",
        "num a2sf"
    ],
    "num_a2_SRF": [
        "num_a2_srf",
        "num a2 srf",
        "bottom",
        "layer"
    ],
    "num_a2": [
        "concentration",
        "num_a2",
        "num a2"
    ],
    "num_a3SF": [
        "num a3sf",
        "dust",
        "emission",
        "num_a3sf",
        "surface"
    ],
    "num_a3_SRF": [
        "layer",
        "num_a3_srf",
        "num a3 srf",
        "bottom"
    ],
    "num_a3": [
        "num a3",
        "concentration",
        "num_a3"
    ],
    "num_a4_CLXF": [
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "num_a4_clxf",
        "external",
        "num a4 clxf"
    ],
    "num_a4_CMXF": [
        "num a4 cmxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "num_a4_cmxf",
        "external"
    ],
    "num_a4DDF": [
        "grav",
        "num a4ddf",
        "deposition",
        "dry",
        "num_a4ddf",
        "flux",
        "bottom"
    ],
    "num_a4SFWET": [
        "num_a4sfwet",
        "deposition",
        "wet",
        "num a4sfwet",
        "flux",
        "surface"
    ],
    "num_a4_SRF": [
        "layer",
        "num_a4_srf",
        "num a4 srf",
        "bottom"
    ],
    "num_a4": [
        "num_a4",
        "concentration",
        "num a4"
    ],
    "num_c4DDF": [
        "num c4ddf",
        "grav",
        "deposition",
        "dry",
        "num_c4ddf",
        "flux",
        "bottom"
    ],
    "num_c4SFWET": [
        "deposition",
        "num c4sfwet",
        "wet",
        "num_c4sfwet",
        "flux",
        "surface"
    ],
    "num_c4": [
        "num_c4",
        "cloud",
        "num c4",
        "water"
    ],
    "NUMICE": [
        "ice",
        "averaged",
        "numice",
        "cloud",
        "box",
        "grid"
    ],
    "NUMRAI": [
        "averaged",
        "number",
        "box",
        "numrai",
        "grid",
        "rain"
    ],
    "NUMSNO": [
        "averaged",
        "snow",
        "numsno",
        "number",
        "box",
        "grid"
    ],
    "O3": [
        "prescribed",
        "tracer",
        "constituent"
    ],
    "OCNFRAC": [
        "ocnfrac",
        "covered",
        "ocean",
        "area",
        "fraction",
        "sfc"
    ],
    "OH": [
        "prescribed",
        "tracer",
        "constituent"
    ],
    "OMEGAT": [
        "omegat",
        "vertical",
        "flux",
        "heat"
    ],
    "pom_a1_SRF": [
        "layer",
        "pom a1 srf",
        "pom_a1_srf",
        "bottom"
    ],
    "pom_a1": [
        "pom a1",
        "concentration",
        "pom_a1"
    ],
    "pom_a4_CLXF": [
        "pom_a4_clxf",
        "pom a4 clxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "external"
    ],
    "pom_a4_CMXF": [
        "pom a4 cmxf",
        "pom_a4_cmxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "external"
    ],
    "pom_a4DDF": [
        "pom a4ddf",
        "grav",
        "deposition",
        "dry",
        "pom_a4ddf",
        "flux",
        "bottom"
    ],
    "pom_a4SFWET": [
        "pom a4sfwet",
        "deposition",
        "wet",
        "pom_a4sfwet",
        "flux",
        "surface"
    ],
    "pom_a4_SRF": [
        "pom a4 srf",
        "layer",
        "bottom",
        "pom_a4_srf"
    ],
    "pom_a4": [
        "concentration",
        "pom a4",
        "pom_a4"
    ],
    "pom_c4DDF": [
        "pom_c4ddf",
        "grav",
        "deposition",
        "dry",
        "pom c4ddf",
        "flux",
        "bottom"
    ],
    "pom_c4SFWET": [
        "pom c4sfwet",
        "deposition",
        "pom_c4sfwet",
        "wet",
        "flux",
        "surface"
    ],
    "pom_c4": [
        "pom_c4",
        "pom c4",
        "water",
        "cloud"
    ],
    "PTEQ": [
        "total",
        "physics",
        "pteq",
        "tendency"
    ],
    "PTTEND": [
        "total",
        "pttend",
        "tendency",
        "physics"
    ],
    "QFLX": [
        "water",
        "flux",
        "surface",
        "qflx"
    ],
    "QRAIN": [
        "precipitation",
        "rainfall",
        "diagnostic",
        "qrain",
        "mixing",
        "grid",
        "mean",
        "rain"
    ],
    "QRLC": [
        "qrlc",
        "longwave",
        "heating",
        "clearsky",
        "rate"
    ],
    "QRSC": [
        "heating",
        "solar",
        "clearsky",
        "qrsc",
        "rate"
    ],
    "QT": [
        "total",
        "ratio",
        "mixing",
        "water"
    ],
    "RAD_ICE": [
        "ice",
        "rad_ice",
        "sad",
        "rad ice"
    ],
    "RAD_LNAT": [
        "rad lnat",
        "large",
        "rad_lnat",
        "nat",
        "radius"
    ],
    "RAD_SULFC": [
        "rad_sulfc",
        "sulfate",
        "rad sulfc",
        "sad",
        "chemical"
    ],
    "RAINQM": [
        "precipitation",
        "rainfall",
        "averaged",
        "box",
        "grid",
        "rainqm",
        "rain",
        "amount"
    ],
    "RCM_CLUBB": [
        "rcm clubb",
        "rcm_clubb",
        "water",
        "cloud",
        "ratio",
        "mixing"
    ],
    "RCMINLAYER_CLUBB": [
        "layer",
        "rcminlayer clubb",
        "water",
        "cloud",
        "rcminlayer_clubb"
    ],
    "RCMTEND_CLUBB": [
        "tendency",
        "water",
        "rcmtend_clubb",
        "rcmtend clubb",
        "cloud",
        "liquid"
    ],
    "REFF_AERO": [
        "aerosol",
        "effective",
        "reff_aero",
        "reff aero",
        "radius"
    ],
    "RELVAR": [
        "relative",
        "water",
        "variance",
        "relvar",
        "cloud"
    ],
    "RHO_CLUBB": [
        "rho_clubb",
        "rho clubb",
        "air",
        "density"
    ],
    "RIMTEND_CLUBB": [
        "ice",
        "tendency",
        "rimtend_clubb",
        "cloud",
        "rimtend clubb"
    ],
    "RTP2_CLUBB": [
        "moisture",
        "rtp2_clubb",
        "variance",
        "rtp2 clubb"
    ],
    "RTPTHLP_CLUBB": [
        "temp",
        "rtpthlp_clubb",
        "covariance",
        "rtpthlp clubb",
        "moist"
    ],
    "RVMTEND_CLUBB": [
        "rvmtend_clubb",
        "tendency",
        "water",
        "rvmtend clubb",
        "vapor"
    ],
    "SAD_AERO": [
        "aerosol",
        "sad_aero",
        "area",
        "sad aero",
        "surface",
        "density"
    ],
    "SAD_ICE": [
        "ice",
        "aerosol",
        "water",
        "sad",
        "sad ice",
        "sad_ice"
    ],
    "SAD_LNAT": [
        "aerosol",
        "sad_lnat",
        "large",
        "mode",
        "sad",
        "nat",
        "sad lnat"
    ],
    "SAD_SULFC": [
        "chemical",
        "aerosol",
        "sulfate",
        "sad",
        "sad sulfc",
        "sad_sulfc"
    ],
    "SAD_TROP": [
        "tropospheric",
        "aerosol",
        "sad",
        "sad_trop",
        "sad trop"
    ],
    "SFbc_a1": [
        "flux",
        "surface",
        "sfbc a1",
        "sfbc_a1"
    ],
    "SFbc_a4": [
        "sfbc_a4",
        "flux",
        "surface",
        "sfbc a4"
    ],
    "SFCO2_LND": [
        "sfco2_lnd",
        "flux",
        "surface",
        "sfco2 lnd"
    ],
    "SFCO2_OCN": [
        "sfco2_ocn",
        "sfco2 ocn",
        "flux",
        "surface"
    ],
    "SFDMS": [
        "dms",
        "sfdms",
        "flux",
        "surface"
    ],
    "SFdst_a1": [
        "temp",
        "sfdst_a1",
        "sfdst a1",
        "temperature",
        "flux",
        "surface",
        "thermal"
    ],
    "SFdst_a2": [
        "sfdst a2",
        "temp",
        "sfdst_a2",
        "temperature",
        "flux",
        "surface",
        "thermal"
    ],
    "SFdst_a3": [
        "sfdst_a3",
        "temp",
        "sfdst a3",
        "temperature",
        "flux",
        "surface",
        "thermal"
    ],
    "SFH2O2": [
        "flux",
        "sfh2o2",
        "surface"
    ],
    "SFH2SO4": [
        "sfh2so4",
        "flux",
        "surface"
    ],
    "SFncl_a1": [
        "sfncl a1",
        "flux",
        "surface",
        "sfncl_a1"
    ],
    "SFncl_a2": [
        "flux",
        "sfncl_a2",
        "surface",
        "sfncl a2"
    ],
    "SFncl_a3": [
        "sfncl_a3",
        "flux",
        "sfncl a3",
        "surface"
    ],
    "SFnum_a1": [
        "sfnum a1",
        "flux",
        "surface",
        "sfnum_a1"
    ],
    "SFnum_a2": [
        "flux",
        "surface",
        "sfnum_a2",
        "sfnum a2"
    ],
    "SFnum_a3": [
        "sfnum a3",
        "flux",
        "surface",
        "sfnum_a3"
    ],
    "SFnum_a4": [
        "sfnum a4",
        "flux",
        "surface",
        "sfnum_a4"
    ],
    "SFpom_a1": [
        "flux",
        "surface",
        "sfpom a1",
        "sfpom_a1"
    ],
    "SFpom_a4": [
        "flux",
        "sfpom a4",
        "sfpom_a4",
        "surface"
    ],
    "SFSO2": [
        "flux",
        "sfso2",
        "surface"
    ],
    "SFso4_a1": [
        "sfso4_a1",
        "flux",
        "surface",
        "sfso4 a1"
    ],
    "SFso4_a2": [
        "flux",
        "surface",
        "sfso4_a2",
        "sfso4 a2"
    ],
    "SFso4_a3": [
        "flux",
        "surface",
        "sfso4 a3",
        "sfso4_a3"
    ],
    "SFsoa_a1": [
        "flux",
        "sfsoa a1",
        "surface",
        "sfsoa_a1"
    ],
    "SFsoa_a2": [
        "flux",
        "sfsoa a2",
        "sfsoa_a2",
        "surface"
    ],
    "SFSOAG": [
        "flux",
        "surface",
        "sfsoag",
        "soag"
    ],
    "SL": [
        "water",
        "energy",
        "liquid",
        "static"
    ],
    "SNOWHICE": [
        "snowhice",
        "ice",
        "snow",
        "depth",
        "over"
    ],
    "SNOWHLND": [
        "water",
        "snow",
        "snowhlnd",
        "depth",
        "equivalent"
    ],
    "SNOWQM": [
        "averaged",
        "snowqm",
        "snow",
        "box",
        "grid",
        "amount"
    ],
    "SO2_CHML": [
        "loss",
        "so2_chml",
        "so2 chml",
        "chemical",
        "rate"
    ],
    "SO2_CHMP": [
        "so2 chmp",
        "so2_chmp",
        "production",
        "chemical",
        "rate"
    ],
    "SO2_CLXF": [
        "so2_clxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "so2 clxf",
        "external"
    ],
    "SO2_CMXF": [
        "so2 cmxf",
        "for",
        "vertically",
        "forcing",
        "so2_cmxf",
        "intergrated",
        "external"
    ],
    "SO2_SRF": [
        "layer",
        "so2_srf",
        "bottom",
        "so2 srf"
    ],
    "SO2": [
        "concentration",
        "so2"
    ],
    "SO2_XFRC": [
        "so2 xfrc",
        "for",
        "forcing",
        "so2_xfrc",
        "external"
    ],
    "so4_a1_CHMP": [
        "so4 a1 chmp",
        "production",
        "chemical",
        "rate",
        "so4_a1_chmp"
    ],
    "so4_a1_CLXF": [
        "so4_a1_clxf",
        "for",
        "vertically",
        "forcing",
        "so4 a1 clxf",
        "intergrated",
        "external"
    ],
    "so4_a1_CMXF": [
        "so4_a1_cmxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "so4 a1 cmxf",
        "external"
    ],
    "so4_a1_sfgaex1": [
        "aerosol",
        "so4 a1 sfgaex1",
        "primary",
        "gas",
        "column",
        "exchange",
        "so4_a1_sfgaex1"
    ],
    "so4_a1_SRF": [
        "layer",
        "so4 a1 srf",
        "so4_a1_srf",
        "bottom"
    ],
    "so4_a1": [
        "so4_a1",
        "concentration",
        "so4 a1"
    ],
    "so4_a2_CHMP": [
        "so4 a2 chmp",
        "so4_a2_chmp",
        "production",
        "chemical",
        "rate"
    ],
    "so4_a2_CLXF": [
        "for",
        "vertically",
        "forcing",
        "so4 a2 clxf",
        "intergrated",
        "so4_a2_clxf",
        "external"
    ],
    "so4_a2_CMXF": [
        "so4 a2 cmxf",
        "for",
        "vertically",
        "forcing",
        "intergrated",
        "so4_a2_cmxf",
        "external"
    ],
    "so4_a2_sfgaex1": [
        "aerosol",
        "so4 a2 sfgaex1",
        "primary",
        "gas",
        "column",
        "exchange",
        "so4_a2_sfgaex1"
    ],
    "so4_a2_sfnnuc1": [
        "new",
        "tendency",
        "nucleation",
        "particle",
        "so4 a2 sfnnuc1",
        "column",
        "so4_a2_sfnnuc1"
    ],
    "so4_a2_SRF": [
        "so4 a2 srf",
        "so4_a2_srf",
        "bottom",
        "layer"
    ],
    "so4_a2": [
        "so4 a2",
        "so4_a2",
        "concentration"
    ],
    "so4_a3_sfgaex1": [
        "aerosol",
        "so4 a3 sfgaex1",
        "primary",
        "gas",
        "so4_a3_sfgaex1",
        "column",
        "exchange"
    ],
    "so4_a3_SRF": [
        "layer",
        "so4 a3 srf",
        "bottom",
        "so4_a3_srf"
    ],
    "so4_a3": [
        "concentration",
        "so4_a3",
        "so4 a3"
    ],
    "so4_c1AQH2SO4": [
        "so4_c1aqh2so4",
        "chemistry",
        "so4 c1aqh2so4",
        "aqueous",
        "phase"
    ],
    "so4_c1AQSO4": [
        "so4 c1aqso4",
        "chemistry",
        "aqueous",
        "phase",
        "so4_c1aqso4"
    ],
    "so4_c2AQH2SO4": [
        "so4 c2aqh2so4",
        "chemistry",
        "aqueous",
        "so4_c2aqh2so4",
        "phase"
    ],
    "so4_c2AQSO4": [
        "chemistry",
        "aqueous",
        "so4 c2aqso4",
        "phase",
        "so4_c2aqso4"
    ],
    "so4_c3AQH2SO4": [
        "so4_c3aqh2so4",
        "so4 c3aqh2so4",
        "chemistry",
        "aqueous",
        "phase"
    ],
    "so4_c3AQSO4": [
        "so4_c3aqso4",
        "chemistry",
        "aqueous",
        "so4 c3aqso4",
        "phase"
    ],
    "soa_a1_SRF": [
        "layer",
        "soa_a1_srf",
        "soa a1 srf",
        "bottom"
    ],
    "soa_a1": [
        "soa_a1",
        "soa a1",
        "concentration"
    ],
    "soa_a2_SRF": [
        "layer",
        "soa_a2_srf",
        "bottom",
        "soa a2 srf"
    ],
    "soa_a2": [
        "soa a2",
        "soa_a2",
        "concentration"
    ],
    "SOAG_SRF": [
        "layer",
        "soag_srf",
        "soag srf",
        "soag",
        "bottom"
    ],
    "SOAG": [
        "concentration",
        "soag"
    ],
    "SSAVIS": [
        "aerosol",
        "single",
        "scatter",
        "day",
        "ssavis",
        "albedo"
    ],
    "SST": [
        "sst",
        "surface",
        "temperature",
        "potential"
    ],
    "STEND_CLUBB": [
        "stend_clubb",
        "tendency",
        "temperature",
        "stend clubb"
    ],
    "TAQ": [
        "tendency",
        "vert",
        "taq",
        "fixer",
        "horz"
    ],
    "TBRY": [
        "volume",
        "inorg",
        "tbry",
        "org",
        "total",
        "mixing"
    ],
    "TCLY": [
        "volume",
        "inorg",
        "org",
        "tcly",
        "total",
        "mixing"
    ],
    "TGCLDCWP": [
        "tgcldcwp",
        "water",
        "total",
        "cloud",
        "box",
        "grid"
    ],
    "THLP2_CLUBB": [
        "variance",
        "thlp2_clubb",
        "temperature",
        "thlp2 clubb"
    ],
    "TH": [
        "temperature",
        "potential"
    ],
    "TMCO2": [
        "tmco2",
        "column",
        "burden"
    ],
    "TMDMS": [
        "tmdms",
        "burden",
        "column",
        "dms"
    ],
    "TMSO2": [
        "burden",
        "column",
        "tmso2"
    ],
    "TMso4_a1": [
        "tmso4 a1",
        "column",
        "burden",
        "tmso4_a1"
    ],
    "TMso4_a2": [
        "tmso4_a2",
        "tmso4 a2",
        "column",
        "burden"
    ],
    "TMso4_a3": [
        "burden",
        "column",
        "tmso4 a3",
        "tmso4_a3"
    ],
    "TOT_CLD_VISTAU": [
        "temp",
        "visible",
        "tot_cld_vistau",
        "total",
        "cloud",
        "temperature",
        "tot cld vistau",
        "gbx",
        "thermal",
        "extinction"
    ],
    "TOTH": [
        "toth",
        "volume",
        "total",
        "ratio",
        "mixing"
    ],
    "TROP_P": [
        "pressure",
        "trop p",
        "tropopause",
        "trop_p"
    ],
    "TROP_T": [
        "trop_t",
        "trop t",
        "temperature",
        "tropopause"
    ],
    "TROP_Z": [
        "height",
        "tropopause",
        "trop z",
        "trop_z"
    ],
    "TTEND_TOT": [
        "tendency",
        "ttend_tot",
        "total",
        "temperature",
        "ttend tot"
    ],
    "TTGWORO": [
        "tendency",
        "drag",
        "wave",
        "orographic",
        "gravity",
        "ttgworo"
    ],
    "UM_CLUBB": [
        "um_clubb",
        "zonal",
        "um clubb",
        "wind"
    ],
    "UP2_CLUBB": [
        "up2 clubb",
        "velocity",
        "variance",
        "zonal",
        "up2_clubb"
    ],
    "UPWP_CLUBB": [
        "upwp clubb",
        "zonal",
        "momentum",
        "flux",
        "upwp_clubb"
    ],
    "UTEND_CLUBB": [
        "tendency",
        "wind",
        "utend_clubb",
        "utend clubb"
    ],
    "UU": [
        "zonal",
        "velocity",
        "squared"
    ],
    "VM_CLUBB": [
        "meridional",
        "vm clubb",
        "wind",
        "vm_clubb"
    ],
    "VP2_CLUBB": [
        "velocity",
        "meridional",
        "vp2 clubb",
        "variance",
        "vp2_clubb"
    ],
    "VPWP_CLUBB": [
        "meridional",
        "vpwp clubb",
        "momentum",
        "flux",
        "vpwp_clubb"
    ],
    "VTEND_CLUBB": [
        "tendency",
        "wind",
        "vtend_clubb",
        "vtend clubb"
    ],
    "VU": [
        "meridional",
        "flux",
        "zonal",
        "momentum"
    ],
    "VV": [
        "meridional",
        "velocity",
        "squared"
    ],
    "WD_H2O2": [
        "vertical",
        "deposition",
        "wd_h2o2",
        "wet",
        "wd h2o2",
        "integrated",
        "flux"
    ],
    "WD_H2SO4": [
        "vertical",
        "deposition",
        "wet",
        "wd_h2so4",
        "integrated",
        "flux",
        "wd h2so4"
    ],
    "WD_SO2": [
        "vertical",
        "wd_so2",
        "deposition",
        "wet",
        "wd so2",
        "integrated",
        "flux"
    ],
    "wet_deposition_NHx_as_N": [
        "temp",
        "nhx",
        "deposition",
        "wet_deposition_nhx_as_n",
        "wet deposition nhx as n",
        "wet",
        "temperature",
        "thermal"
    ],
    "wet_deposition_NOy_as_N": [
        "temp",
        "noy",
        "wet_deposition_noy_as_n",
        "deposition",
        "wet",
        "wet deposition noy as n",
        "temperature",
        "thermal"
    ],
    "WP2_CLUBB": [
        "velocity",
        "vertical",
        "wp2 clubb",
        "variance",
        "wp2_clubb"
    ],
    "WP3_CLUBB": [
        "velocity",
        "vertical",
        "wp3 clubb",
        "moment",
        "third",
        "wp3_clubb"
    ],
    "WPRCP_CLUBB": [
        "water",
        "wprcp_clubb",
        "liquid",
        "flux",
        "wprcp clubb"
    ],
    "WPRTP_CLUBB": [
        "moisture",
        "flux",
        "wprtp_clubb",
        "wprtp clubb"
    ],
    "WPTHLP_CLUBB": [
        "flux",
        "wpthlp_clubb",
        "wpthlp clubb",
        "heat"
    ],
    "WPTHVP_CLUBB": [
        "wpthvp_clubb",
        "flux",
        "wpthvp clubb",
        "buoyancy"
    ],
    "WTHzm": [
        "heat",
        "vertical",
        "wthzm",
        "zon",
        "flux",
        "mean"
    ],
    "ZM_CLUBB": [
        "zm clubb",
        "zm_clubb",
        "heights",
        "momentum"
    ],
    "ZMDQ": [
        "tendency",
        "zmdq",
        "zhang",
        "convection",
        "mcfarlane",
        "moist"
    ],
    "ZMDT": [
        "zmdt",
        "tendency",
        "zhang",
        "convection",
        "mcfarlane",
        "moist"
    ],
    "ZMMTT": [
        "tendency",
        "convective",
        "transport",
        "momentum",
        "zmmtt"
    ],
    "ZMMU": [
        "mass",
        "zmmu",
        "convection",
        "flux",
        "updraft"
    ],
    "ZT_CLUBB": [
        "thermodynamic",
        "temp",
        "heights",
        "temperature",
        "zt_clubb",
        "thermal",
        "zt clubb"
    ],
    "artm": [
        "air",
        "artm",
        "temperature",
        "annual",
        "mean"
    ],
    "smb": [
        "surface",
        "balance",
        "mass",
        "smb"
    ],
    "thk": [
        "ice",
        "thk",
        "thickness"
    ],
    "topg": [
        "bedrock",
        "topography",
        "topg"
    ],
    "usurf": [
        "ice",
        "usurf",
        "elevation",
        "upper",
        "surface"
    ],
    "congel_d": [
        "growth",
        "congel d",
        "congelation",
        "ice",
        "congel_d"
    ],
    "daidtd_d": [
        "tendency",
        "daidtd d",
        "daidtd_d",
        "dynamics",
        "area"
    ],
    "daidtt_d": [
        "tendency",
        "temp",
        "daidtt d",
        "temperature",
        "area",
        "thermal",
        "daidtt_d",
        "thermo"
    ],
    "dvidtd_d": [
        "dvidtd_d",
        "tendency",
        "dvidtd d",
        "volume",
        "dynamics"
    ],
    "dvidtt_d": [
        "dvidtt d",
        "tendency",
        "temp",
        "volume",
        "temperature",
        "thermal",
        "dvidtt_d",
        "thermo"
    ],
    "frazil_d": [
        "growth",
        "ice",
        "frazil d",
        "frazil_d",
        "frazil"
    ],
    "fswabs_d": [
        "ice",
        "absorbed",
        "snow",
        "solar",
        "fswabs_d",
        "ocn",
        "fswabs d"
    ],
    "fswdn_d": [
        "down",
        "fswdn_d",
        "fswdn d",
        "solar",
        "flux"
    ],
    "fswup_d": [
        "solar",
        "upward",
        "fswup d",
        "flux",
        "fswup_d"
    ],
    "FYarea_d": [
        "ice",
        "fyarea d",
        "fyarea_d",
        "area",
        "year",
        "first"
    ],
    "hs_d": [
        "cell",
        "snow",
        "hs_d",
        "grid",
        "mean",
        "hs d",
        "thickness"
    ],
    "meltb_d": [
        "melt",
        "ice",
        "meltb_d",
        "meltb d",
        "basal"
    ],
    "meltl_d": [
        "melt",
        "meltl d",
        "ice",
        "lateral",
        "meltl_d"
    ],
    "melts_d": [
        "melt",
        "top",
        "melts_d",
        "snow",
        "melts d"
    ],
    "meltt_d": [
        "melt",
        "ice",
        "top",
        "temp",
        "meltt d",
        "temperature",
        "thermal",
        "meltt_d"
    ],
    "rain_d": [
        "rain d",
        "cpl",
        "rainfall",
        "precipitation",
        "rain_d",
        "rate",
        "rain"
    ],
    "snoice_d": [
        "ice",
        "formation",
        "snow",
        "snoice d",
        "snoice_d"
    ],
    "snow_d": [
        "snow d",
        "cpl",
        "snowfall",
        "rate",
        "snow_d"
    ],
    "snowfrac_d": [
        "cell",
        "snow",
        "snowfrac_d",
        "fraction",
        "grid",
        "mean",
        "snowfrac d"
    ],
    "strairx_d": [
        "ice",
        "stress",
        "atm",
        "strairx d",
        "strairx_d"
    ],
    "strairy_d": [
        "ice",
        "strairy_d",
        "stress",
        "atm",
        "strairy d"
    ],
    "strintx_d": [
        "strintx_d",
        "ice",
        "stress",
        "internal",
        "strintx d"
    ],
    "strinty_d": [
        "ice",
        "stress",
        "strinty_d",
        "strinty d",
        "internal"
    ],
    "strocnx_d": [
        "ice",
        "stress",
        "strocnx d",
        "ocean",
        "strocnx_d"
    ],
    "strocny_d": [
        "ice",
        "stress",
        "strocny_d",
        "ocean",
        "strocny d"
    ],
    "vicen_d": [
        "ice",
        "volume",
        "vicen_d",
        "vicen d",
        "categories"
    ],
    "vsnon_d": [
        "ice",
        "vsnon d",
        "snow",
        "vsnon_d",
        "depth",
        "categories"
    ],
    "divu": [
        "divu",
        "divergence",
        "rate",
        "strain"
    ],
    "fhocn": [
        "ice",
        "heat",
        "cpl",
        "fhocn",
        "ocn",
        "flux"
    ],
    "flat_ai": [
        "latent",
        "heat",
        "flat_ai",
        "temp",
        "flat ai",
        "temperature",
        "flux",
        "thermal"
    ],
    "flat": [
        "latent",
        "heat",
        "cpl",
        "flat",
        "flux"
    ],
    "flwdn": [
        "down",
        "flux",
        "longwave",
        "flwdn"
    ],
    "flwup": [
        "cpl",
        "longwave",
        "upward",
        "flwup",
        "flux"
    ],
    "fsens_ai": [
        "heat",
        "fsens ai",
        "fsens_ai",
        "sensible",
        "flux"
    ],
    "fsens": [
        "heat",
        "cpl",
        "fsens",
        "sensible",
        "flux"
    ],
    "fswabs": [
        "ice",
        "fswabs",
        "absorbed",
        "snow",
        "solar",
        "ocn"
    ],
    "fswintn": [
        "fswintn",
        "absorbed",
        "internal",
        "shortwave",
        "categories"
    ],
    "fswsfcn": [
        "fswsfcn",
        "absorbed",
        "shortwave",
        "surface",
        "categories"
    ],
    "fswthrun": [
        "shortwave",
        "fswthrun",
        "categories",
        "penetrating"
    ],
    "fswup": [
        "flux",
        "solar",
        "upward",
        "fswup"
    ],
    "FYarea": [
        "ice",
        "area",
        "year",
        "fyarea",
        "first"
    ],
    "melts": [
        "melt",
        "top",
        "snow",
        "melts"
    ],
    "rain": [
        "precipitation",
        "cpl",
        "rainfall",
        "rate",
        "rain"
    ],
    "shear": [
        "shear",
        "rate",
        "strain"
    ],
    "sig1": [
        "sig1",
        "norm",
        "stress",
        "principal"
    ],
    "sig2": [
        "sig2",
        "norm",
        "stress",
        "principal"
    ],
    "snoice": [
        "ice",
        "snow",
        "snoice",
        "formation"
    ],
    "snow": [
        "rate",
        "snow",
        "snowfall",
        "cpl"
    ],
    "strairx": [
        "strairx",
        "ice",
        "stress",
        "atm"
    ],
    "strairy": [
        "ice",
        "atm",
        "stress",
        "strairy"
    ],
    "strcorx": [
        "coriolis",
        "strcorx",
        "stress"
    ],
    "strcory": [
        "coriolis",
        "strcory",
        "stress"
    ],
    "strength": [
        "strength",
        "ice",
        "compressive"
    ],
    "strintx": [
        "ice",
        "stress",
        "strintx",
        "internal"
    ],
    "strinty": [
        "ice",
        "strinty",
        "stress",
        "internal"
    ],
    "strocnx": [
        "strocnx",
        "ocean",
        "ice",
        "stress"
    ],
    "strocny": [
        "ice",
        "ocean",
        "strocny",
        "stress"
    ],
    "strtltx": [
        "strtltx",
        "stress",
        "sea",
        "sfc",
        "tilt"
    ],
    "strtlty": [
        "stress",
        "strtlty",
        "sea",
        "sfc",
        "tilt"
    ],
    "Tsfc": [
        "ice",
        "tsfc",
        "snow",
        "temperature",
        "surface"
    ],
    "uvel": [
        "uvel",
        "velocity",
        "ice"
    ],
    "vicen": [
        "ice",
        "vicen",
        "categories",
        "volume"
    ],
    "vsnon": [
        "ice",
        "snow",
        "depth",
        "vsnon",
        "categories"
    ],
    "vvel": [
        "vvel",
        "velocity",
        "ice"
    ],
    "aice_d": [
        "ice",
        "aggregate",
        "aice d",
        "area",
        "aice_d"
    ],
    "aicen_d": [
        "ice",
        "area",
        "aicen d",
        "categories",
        "aicen_d"
    ],
    "apond_ai_d": [
        "apond_ai_d",
        "melt",
        "cell",
        "pond",
        "apond ai d",
        "fraction",
        "grid"
    ],
    "fswthru_d": [
        "ice",
        "cpl",
        "thru",
        "fswthru_d",
        "ocean",
        "fswthru d"
    ],
    "hi_d": [
        "cell",
        "ice",
        "hi_d",
        "hi d",
        "grid",
        "mean",
        "thickness"
    ],
    "ice_present_d": [
        "ice present d",
        "temp",
        "that",
        "avg",
        "fraction",
        "temperature",
        "time",
        "ice_present_d",
        "thermal",
        "interval"
    ],
    "sisnthick_d": [
        "ice",
        "snow",
        "sisnthick_d",
        "sisnthick d",
        "sea",
        "thickness"
    ],
    "sispeed_d": [
        "ice",
        "speed",
        "sispeed_d",
        "sispeed d"
    ],
    "sitemptop_d": [
        "ice",
        "temp",
        "sitemptop d",
        "temperature",
        "sea",
        "sitemptop_d",
        "surface",
        "thermal"
    ],
    "sithick_d": [
        "ice",
        "sithick d",
        "sithick_d",
        "sea",
        "thickness"
    ],
    "siu_d": [
        "ice",
        "velocity",
        "siu_d",
        "component",
        "siu d"
    ],
    "siv_d": [
        "ice",
        "velocity",
        "siv d",
        "component",
        "siv_d"
    ],
    "aicen": [
        "area",
        "ice",
        "categories",
        "aicen"
    ],
    "aice": [
        "area",
        "ice",
        "aggregate",
        "aice"
    ],
    "albsni": [
        "ice",
        "broad",
        "albsni",
        "snow",
        "albedo",
        "band"
    ],
    "alidf_ai": [
        "alidf_ai",
        "diffuse",
        "near",
        "albedo",
        "alidf ai"
    ],
    "alidr_ai": [
        "direct",
        "near",
        "albedo",
        "alidr ai",
        "alidr_ai"
    ],
    "alvdf_ai": [
        "alvdf_ai",
        "diffuse",
        "visible",
        "alvdf ai",
        "albedo"
    ],
    "alvdr_ai": [
        "alvdr_ai",
        "alvdr ai",
        "visible",
        "direct",
        "albedo"
    ],
    "apeff_ai": [
        "apeff_ai",
        "effective",
        "radiation",
        "pond",
        "area",
        "fraction",
        "apeff ai"
    ],
    "apond_ai": [
        "melt",
        "cell",
        "apond_ai",
        "pond",
        "apond ai",
        "fraction",
        "grid"
    ],
    "ardg": [
        "ice",
        "ardg",
        "ridged",
        "area",
        "fraction"
    ],
    "congel": [
        "growth",
        "ice",
        "congelation",
        "congel"
    ],
    "dagedtd": [
        "dagedtd",
        "dynamics",
        "tendency",
        "age"
    ],
    "dagedtt": [
        "age",
        "tendency",
        "thermo",
        "dagedtt"
    ],
    "daidtd": [
        "daidtd",
        "dynamics",
        "tendency",
        "area"
    ],
    "daidtt": [
        "area",
        "thermo",
        "tendency",
        "daidtt"
    ],
    "dvidtd": [
        "tendency",
        "dynamics",
        "dvidtd",
        "volume"
    ],
    "dvidtt": [
        "tendency",
        "thermo",
        "dvidtt",
        "volume"
    ],
    "evap": [
        "evaporative",
        "cpl",
        "water",
        "flux",
        "evap"
    ],
    "frazil": [
        "growth",
        "frazil",
        "ice"
    ],
    "fresh": [
        "ice",
        "cpl",
        "flx",
        "fresh",
        "freshwtr",
        "ocn"
    ],
    "fsalt": [
        "ice",
        "cpl",
        "salt",
        "ocn",
        "flux",
        "fsalt"
    ],
    "fswdn": [
        "down",
        "flux",
        "solar",
        "fswdn"
    ],
    "fswthru": [
        "fswthru",
        "ice",
        "cpl",
        "thru",
        "ocean"
    ],
    "hi": [
        "cell",
        "ice",
        "grid",
        "mean",
        "thickness"
    ],
    "hs": [
        "cell",
        "snow",
        "grid",
        "mean",
        "thickness"
    ],
    "ice_present": [
        "that",
        "avg",
        "ice_present",
        "ice present",
        "fraction",
        "time",
        "interval"
    ],
    "meltb": [
        "melt",
        "ice",
        "meltb",
        "basal"
    ],
    "meltl": [
        "lateral",
        "ice",
        "meltl",
        "melt"
    ],
    "meltt": [
        "melt",
        "ice",
        "top",
        "meltt"
    ],
    "siage": [
        "ice",
        "siage",
        "sea",
        "age"
    ],
    "sialb": [
        "ice",
        "albedo",
        "sialb",
        "sea"
    ],
    "sicompstren": [
        "ice",
        "sicompstren",
        "strength",
        "sea",
        "compressive"
    ],
    "sidconcdyn": [
        "ice",
        "from",
        "change",
        "area",
        "sea",
        "sidconcdyn"
    ],
    "sidconcth": [
        "ice",
        "sidconcth",
        "from",
        "change",
        "area",
        "sea"
    ],
    "sidmassdyn": [
        "ice",
        "mass",
        "from",
        "change",
        "sea",
        "sidmassdyn"
    ],
    "sidmassevapsubl": [
        "ice",
        "mass",
        "from",
        "change",
        "sea",
        "sidmassevapsubl"
    ],
    "sidmassgrowthbot": [
        "ice",
        "mass",
        "from",
        "change",
        "sea",
        "sidmassgrowthbot"
    ],
    "sidmassgrowthwat": [
        "ice",
        "mass",
        "sidmassgrowthwat",
        "from",
        "change",
        "sea"
    ],
    "sidmasslat": [
        "ice",
        "mass",
        "lateral",
        "sidmasslat",
        "change",
        "sea"
    ],
    "sidmassmeltbot": [
        "ice",
        "mass",
        "sidmassmeltbot",
        "change",
        "sea",
        "bottom"
    ],
    "sidmassmelttop": [
        "ice",
        "top",
        "mass",
        "sidmassmelttop",
        "change",
        "sea"
    ],
    "sidmasssi": [
        "ice",
        "mass",
        "sidmasssi",
        "from",
        "change",
        "sea"
    ],
    "sidmassth": [
        "ice",
        "mass",
        "from",
        "change",
        "sidmassth",
        "sea"
    ],
    "sidmasstranx": [
        "ice",
        "snow",
        "component",
        "and",
        "sea",
        "sidmasstranx"
    ],
    "sidmasstrany": [
        "ice",
        "sidmasstrany",
        "snow",
        "component",
        "and",
        "sea"
    ],
    "sidragtop": [
        "ice",
        "drag",
        "atmospheric",
        "sidragtop",
        "sea",
        "over"
    ],
    "sifb": [
        "ice",
        "above",
        "sifb",
        "freeboard",
        "sea"
    ],
    "siflcondbot": [
        "heat",
        "siflcondbot",
        "sea",
        "conductive",
        "flux",
        "bottom"
    ],
    "siflcondtop": [
        "top",
        "heat",
        "siflcondtop",
        "sea",
        "flux",
        "conductive"
    ],
    "siflfwbot": [
        "fresh",
        "water",
        "from",
        "siflfwbot",
        "sea",
        "flux"
    ],
    "siflfwdrain": [
        "precipitation",
        "rainfall",
        "through",
        "fresh",
        "water",
        "siflfwdrain",
        "drainage",
        "sea",
        "rain"
    ],
    "sifllatstop": [
        "latent",
        "heat",
        "sifllatstop",
        "sea",
        "flux",
        "over"
    ],
    "sifllwdtop": [
        "down",
        "longwave",
        "over",
        "sea",
        "flux",
        "sifllwdtop"
    ],
    "sifllwutop": [
        "sifllwutop",
        "longwave",
        "upward",
        "sea",
        "flux",
        "over"
    ],
    "siflsaltbot": [
        "ice",
        "from",
        "siflsaltbot",
        "salt",
        "sea",
        "flux"
    ],
    "siflsenstop": [
        "heat",
        "siflsenstop",
        "sea",
        "sensible",
        "flux",
        "over"
    ],
    "siflsensupbot": [
        "heat",
        "sea",
        "siflsensupbot",
        "sensible",
        "flux",
        "bottom"
    ],
    "siflswdbot": [
        "down",
        "ice",
        "siflswdbot",
        "shortwave",
        "flux",
        "bottom"
    ],
    "siflswdtop": [
        "down",
        "sea",
        "shortwave",
        "flux",
        "over",
        "siflswdtop"
    ],
    "siflswutop": [
        "upward",
        "siflswutop",
        "sea",
        "shortwave",
        "flux",
        "over"
    ],
    "siforcecoriolx": [
        "coriolis",
        "term",
        "siforcecoriolx"
    ],
    "siforcecorioly": [
        "term",
        "coriolis",
        "siforcecorioly"
    ],
    "siforceintstrx": [
        "siforceintstrx",
        "term",
        "stress",
        "internal"
    ],
    "siforceintstry": [
        "term",
        "internal",
        "stress",
        "siforceintstry"
    ],
    "siforcetiltx": [
        "surface",
        "term",
        "sea",
        "tilt",
        "siforcetiltx"
    ],
    "siforcetilty": [
        "siforcetilty",
        "term",
        "tile",
        "sea",
        "surface"
    ],
    "sihc": [
        "ice",
        "heat",
        "content",
        "sihc",
        "sea"
    ],
    "siitdconc": [
        "ice",
        "siitdconc",
        "categories",
        "area"
    ],
    "siitdsnthick": [
        "siitdsnthick",
        "snow",
        "thickness",
        "categories"
    ],
    "siitdthick": [
        "ice",
        "thickness",
        "categories",
        "siitdthick"
    ],
    "sipr": [
        "sipr",
        "ice",
        "rainfall",
        "sea",
        "over"
    ],
    "sirdgthick": [
        "ice",
        "ridge",
        "sirdgthick",
        "sea",
        "thickness"
    ],
    "sisnhc": [
        "content",
        "sisnhc",
        "snow",
        "heat"
    ],
    "sisnthick": [
        "ice",
        "snow",
        "sea",
        "sisnthick",
        "thickness"
    ],
    "sispeed": [
        "sispeed",
        "ice",
        "speed"
    ],
    "sistreave": [
        "sistreave",
        "average",
        "normal",
        "stress"
    ],
    "sistremax": [
        "maximum",
        "sistremax",
        "stress",
        "shear"
    ],
    "sistrxdtop": [
        "ice",
        "stress",
        "atmospheric",
        "component",
        "sea",
        "sistrxdtop"
    ],
    "sistrxubot": [
        "ice",
        "stress",
        "component",
        "ocean",
        "sistrxubot",
        "sea"
    ],
    "sistrydtop": [
        "ice",
        "stress",
        "atmospheric",
        "sistrydtop",
        "component",
        "sea"
    ],
    "sistryubot": [
        "ice",
        "stress",
        "component",
        "ocean",
        "sea",
        "sistryubot"
    ],
    "sitempbot": [
        "ice",
        "temp",
        "sitempbot",
        "temperature",
        "sea",
        "thermal",
        "bottom"
    ],
    "sitempsnic": [
        "interface",
        "ice",
        "sitempsnic",
        "temp",
        "snow",
        "temperature",
        "thermal"
    ],
    "sitemptop": [
        "ice",
        "temp",
        "sitemptop",
        "temperature",
        "sea",
        "surface",
        "thermal"
    ],
    "sithick": [
        "ice",
        "thickness",
        "sea",
        "sithick"
    ],
    "siu": [
        "ice",
        "velocity",
        "siu",
        "component"
    ],
    "siv": [
        "ice",
        "velocity",
        "siv",
        "component"
    ],
    "sndmassmelt": [
        "mass",
        "from",
        "snow",
        "change",
        "sndmassmelt"
    ],
    "sndmasssnf": [
        "mass",
        "from",
        "snow",
        "change",
        "sndmasssnf"
    ],
    "sndmassubl": [
        "mass",
        "from",
        "snow",
        "change",
        "sndmassubl",
        "evaporation"
    ],
    "snowfrac": [
        "cell",
        "snow",
        "grid",
        "fraction",
        "snowfrac",
        "mean"
    ],
    "uatm": [
        "velocity",
        "uatm",
        "atm"
    ],
    "vatm": [
        "vatm",
        "velocity",
        "atm"
    ],
    "ALT": [
        "layer",
        "active",
        "current",
        "alt",
        "thickness"
    ],
    "AR": [
        "autotrophic",
        "respiration"
    ],
    "EFLX_LH_TOT": [
        "latent",
        "heat",
        "eflx lh tot",
        "atm",
        "total",
        "eflx_lh_tot",
        "flux"
    ],
    "FGR12": [
        "heat",
        "soil",
        "between",
        "fgr12",
        "layers",
        "flux"
    ],
    "FIRA": [
        "net",
        "infrared",
        "longwave",
        "radiation",
        "fira"
    ],
    "FSA": [
        "absorbed",
        "radiation",
        "solar",
        "fsa"
    ],
    "FSDSND": [
        "fsdsnd",
        "nir",
        "radiation",
        "solar",
        "direct",
        "incident"
    ],
    "FSDSNI": [
        "nir",
        "diffuse",
        "radiation",
        "solar",
        "fsdsni",
        "incident"
    ],
    "FSDSVD": [
        "fsdsvd",
        "radiation",
        "solar",
        "vis",
        "direct",
        "incident"
    ],
    "FSDSVI": [
        "diffuse",
        "radiation",
        "solar",
        "vis",
        "fsdsvi",
        "incident"
    ],
    "FSH": [
        "heat",
        "correction",
        "not",
        "including",
        "sensible",
        "fsh"
    ],
    "FSM": [
        "melt",
        "heat",
        "snow",
        "fsm",
        "flux"
    ],
    "FSNO": [
        "ground",
        "snow",
        "fsno",
        "covered",
        "fraction"
    ],
    "GPP": [
        "primary",
        "gpp",
        "gross",
        "production"
    ],
    "H2OCAN": [
        "water",
        "intercepted",
        "h2ocan"
    ],
    "H2OSFC": [
        "h2osfc",
        "surface",
        "water",
        "depth"
    ],
    "H2OSNO": [
        "water",
        "h2osno",
        "snow",
        "depth",
        "liquid"
    ],
    "HR": [
        "total",
        "heterotrophic",
        "respiration"
    ],
    "NPP": [
        "npp",
        "primary",
        "net",
        "production"
    ],
    "QDRAI_PERCH": [
        "perched",
        "qdrai_perch",
        "drainage",
        "qdrai perch"
    ],
    "QDRAI": [
        "qdrai",
        "drainage",
        "sub",
        "surface"
    ],
    "QFLX_SNOW_DRAIN": [
        "precipitation",
        "rainfall",
        "pack",
        "from",
        "snow",
        "drainage",
        "qflx_snow_drain",
        "rain",
        "qflx snow drain"
    ],
    "QFLX_SUB_SNOW": [
        "pack",
        "sublimation",
        "from",
        "snow",
        "qflx sub snow",
        "rate",
        "qflx_sub_snow"
    ],
    "QINTR": [
        "qintr",
        "interception"
    ],
    "QOVER": [
        "surface",
        "qover",
        "runoff"
    ],
    "QRUNOFF": [
        "not",
        "runoff",
        "qrunoff",
        "total",
        "including",
        "liquid"
    ],
    "QSNOEVAP": [
        "from",
        "snow",
        "qsnoevap",
        "evaporation"
    ],
    "QSNOFRZ": [
        "qsnofrz",
        "snow",
        "integrated",
        "freezing",
        "column",
        "rate"
    ],
    "QSOIL": [
        "soil",
        "snow",
        "ground",
        "qsoil",
        "evaporation"
    ],
    "QVEGE": [
        "qvege",
        "evaporation",
        "canopy"
    ],
    "QVEGT": [
        "qvegt",
        "transpiration",
        "canopy"
    ],
    "RAIN": [
        "precipitation",
        "rainfall",
        "atmospheric",
        "snow",
        "after",
        "rain"
    ],
    "SNOBCMSL": [
        "layer",
        "top",
        "mass",
        "snow",
        "snobcmsl"
    ],
    "SNOCAN": [
        "snocan",
        "snow",
        "intercepted"
    ],
    "SNOFSRND": [
        "nir",
        "radiation",
        "solar",
        "direct",
        "reflected",
        "snofsrnd"
    ],
    "SNOFSRNI": [
        "nir",
        "snofsrni",
        "diffuse",
        "radiation",
        "solar",
        "reflected"
    ],
    "SNOFSRVD": [
        "radiation",
        "solar",
        "snofsrvd",
        "vis",
        "direct",
        "reflected"
    ],
    "SNOFSRVI": [
        "diffuse",
        "radiation",
        "solar",
        "vis",
        "reflected",
        "snofsrvi"
    ],
    "SNOTXMASS": [
        "layer",
        "mass",
        "snow",
        "snotxmass",
        "temperature",
        "times"
    ],
    "SNOWDP": [
        "snowdp",
        "snow",
        "gridcell",
        "mean",
        "height"
    ],
    "SNOWICE": [
        "ice",
        "snow",
        "snowice"
    ],
    "SNOWLIQ": [
        "water",
        "snowliq",
        "snow",
        "liquid"
    ],
    "SNOW": [
        "atmospheric",
        "after",
        "snow",
        "rain"
    ],
    "SOILICE": [
        "ice",
        "soil",
        "vegetated",
        "only",
        "landunits",
        "soilice"
    ],
    "SOILLIQ": [
        "soil",
        "vegetated",
        "landunits",
        "water",
        "liquid",
        "soilliq"
    ],
    "SOILWATER_10CM": [
        "ice",
        "top",
        "soil",
        "water",
        "soilwater 10cm",
        "liquid",
        "soilwater_10cm"
    ],
    "TG": [
        "ground",
        "temperature"
    ],
    "TLAI": [
        "total",
        "index",
        "tlai",
        "area",
        "projected",
        "leaf"
    ],
    "TOTSOILICE": [
        "soil",
        "cie",
        "vertically",
        "totsoilice",
        "summed",
        "veg"
    ],
    "TOTSOILLIQ": [
        "totsoilliq",
        "soil",
        "water",
        "vertically",
        "liquid",
        "summed"
    ],
    "TREFMNAV": [
        "daily",
        "minimum",
        "trefmnav",
        "average",
        "temperature"
    ],
    "TREFMXAV": [
        "daily",
        "average",
        "trefmxav",
        "maximum",
        "temperature"
    ],
    "TSKIN": [
        "skin",
        "tskin",
        "temperature"
    ],
    "TSOI": [
        "soil",
        "vegetated",
        "only",
        "landunits",
        "tsoi",
        "temperature"
    ],
    "TV": [
        "temperature",
        "vegetation"
    ],
    "TWS": [
        "total",
        "tws",
        "storage",
        "water"
    ],
    "C14_SOILC_vr": [
        "soil",
        "vertically",
        "c14_soilc_vr",
        "c14 soilc vr",
        "resolved"
    ],
    "SOILC_vr": [
        "soilc vr",
        "soil",
        "soilc_vr",
        "vertically",
        "resolved"
    ],
    "SOILN_vr": [
        "soil",
        "vertically",
        "soiln vr",
        "soiln_vr",
        "resolved"
    ],
    "RH2M": [
        "relative",
        "rh2m",
        "humidity"
    ],
    "TSA": [
        "air",
        "tsa",
        "temperature"
    ],
    "H2OSOI": [
        "soil",
        "vegetated",
        "h2osoi",
        "landunits",
        "water",
        "volumetric"
    ],
    "C13_NBP": [
        "c13 nbp",
        "net",
        "c13_nbp",
        "includes",
        "production",
        "fire",
        "biome"
    ],
    "C14_NBP": [
        "net",
        "includes",
        "c14 nbp",
        "c14_nbp",
        "production",
        "fire",
        "biome"
    ],
    "DWT_SEEDN_TO_DEADSTEM": [
        "dwt_seedn_to_deadstem",
        "temp",
        "deadstem",
        "patch",
        "source",
        "seed",
        "level",
        "temperature",
        "dwt seedn to deadstem",
        "thermal"
    ],
    "DWT_SEEDN_TO_LEAF": [
        "dwt seedn to leaf",
        "dwt_seedn_to_leaf",
        "temp",
        "patch",
        "source",
        "seed",
        "level",
        "temperature",
        "leaf",
        "thermal"
    ],
    "EFLX_DYNBAL": [
        "conversion",
        "eflx dynbal",
        "dynamic",
        "cover",
        "change",
        "eflx_dynbal",
        "land"
    ],
    "EFLX_LH_TOT_R": [
        "rural",
        "temp",
        "total",
        "eflx_lh_tot_r",
        "eflx lh tot r",
        "temperature",
        "evaporation",
        "thermal"
    ],
    "ERRH2OSNO": [
        "water",
        "snow",
        "imbalance",
        "depth",
        "liquid",
        "errh2osno"
    ],
    "ERRSEB": [
        "error",
        "conservation",
        "errseb",
        "energy",
        "surface"
    ],
    "ERRSOI": [
        "soil",
        "lake",
        "error",
        "conservation",
        "energy",
        "errsoi"
    ],
    "ERRSOL": [
        "errsol",
        "radiation",
        "solar",
        "error",
        "conservation"
    ],
    "ESAI": [
        "one",
        "stem",
        "exposed",
        "esai",
        "area",
        "sided"
    ],
    "FCOV": [
        "fcov",
        "impermeable",
        "fractional",
        "area"
    ],
    "FFIX_TO_SMINN": [
        "soil",
        "ffix_to_sminn",
        "mineral",
        "living",
        "fixation",
        "ffix to sminn",
        "free"
    ],
    "FGR": [
        "heat",
        "soil",
        "fgr",
        "snow",
        "flux",
        "into"
    ],
    "FIRA_R": [
        "net",
        "rural",
        "infrared",
        "longwave",
        "radiation",
        "fira_r",
        "fira r"
    ],
    "FPI": [
        "fpi",
        "fraction",
        "potential",
        "immobilization"
    ],
    "FROOTC_ALLOC": [
        "root",
        "allocation",
        "frootc alloc",
        "fine",
        "frootc_alloc"
    ],
    "FROOTC_LOSS": [
        "root",
        "fine",
        "loss",
        "frootc loss",
        "frootc_loss"
    ],
    "FROOTC": [
        "frootc",
        "root",
        "fine"
    ],
    "FROOTN": [
        "root",
        "frootn",
        "fine"
    ],
    "FSAT": [
        "table",
        "water",
        "fsat",
        "fractional",
        "area",
        "with"
    ],
    "FSDSNDLN": [
        "nir",
        "radiation",
        "solar",
        "direct",
        "incident",
        "fsdsndln"
    ],
    "FSDSVDLN": [
        "fsdsvdln",
        "radiation",
        "solar",
        "vis",
        "direct",
        "incident"
    ],
    "FSH_G": [
        "heat",
        "fsh g",
        "from",
        "ground",
        "sensible",
        "fsh_g"
    ],
    "FSH_R": [
        "rural",
        "heat",
        "sensible",
        "fsh r",
        "fsh_r"
    ],
    "FSH_V": [
        "heat",
        "from",
        "fsh_v",
        "fsh v",
        "sensible",
        "veg"
    ],
    "FSRNDLN": [
        "nir",
        "radiation",
        "solar",
        "fsrndln",
        "direct",
        "reflected"
    ],
    "FSRVDLN": [
        "radiation",
        "solar",
        "vis",
        "direct",
        "reflected",
        "fsrvdln"
    ],
    "GROSS_NMIN": [
        "gross nmin",
        "gross",
        "gross_nmin",
        "mineralization",
        "rate"
    ],
    "GR": [
        "total",
        "growth",
        "respiration"
    ],
    "H2OSNO_TOP": [
        "layer",
        "top",
        "mass",
        "snow",
        "h2osno top",
        "h2osno_top"
    ],
    "HEAT_FROM_AC": [
        "heat",
        "temp",
        "heat from ac",
        "put",
        "temperature",
        "sensible",
        "flux",
        "heat_from_ac",
        "into",
        "thermal"
    ],
    "HTOP": [
        "htop",
        "top",
        "canopy"
    ],
    "LAISHA": [
        "laisha",
        "index",
        "area",
        "projected",
        "shaded",
        "leaf"
    ],
    "LAISUN": [
        "index",
        "sunlit",
        "area",
        "projected",
        "laisun",
        "leaf"
    ],
    "LAND_USE_FLUX": [
        "land_use_flux",
        "from",
        "cover",
        "total",
        "land",
        "emitted",
        "land use flux"
    ],
    "LEAFC_ALLOC": [
        "leaf",
        "allocation",
        "leafc alloc",
        "leafc_alloc"
    ],
    "LEAFC_LOSS": [
        "leaf",
        "loss",
        "leafc_loss",
        "leafc loss"
    ],
    "LEAFC": [
        "leaf",
        "leafc"
    ],
    "LEAFN": [
        "leaf",
        "leafn"
    ],
    "LITFALL": [
        "leaves",
        "fine",
        "and",
        "litterfall",
        "roots",
        "litfall"
    ],
    "LITR1C": [
        "litr1c"
    ],
    "LITR1C_TO_SOIL1C": [
        "soil",
        "decomp",
        "litter",
        "litr1c_to_soil1c",
        "litr1c to soil1c"
    ],
    "LITR1N": [
        "litr1n"
    ],
    "LITR2C": [
        "litr2c"
    ],
    "LITR2N": [
        "litr2n"
    ],
    "LITR3C": [
        "litr3c"
    ],
    "LITR3N": [
        "litr3n"
    ],
    "LITTERC_LOSS": [
        "litterc loss",
        "loss",
        "litter",
        "litterc_loss"
    ],
    "LIVECROOTC": [
        "live",
        "root",
        "coarse",
        "livecrootc"
    ],
    "LIVECROOTN": [
        "live",
        "root",
        "livecrootn",
        "coarse"
    ],
    "LIVESTEMC": [
        "live",
        "livestemc",
        "stem"
    ],
    "LIVESTEMN": [
        "live",
        "livestemn",
        "stem"
    ],
    "MR": [
        "respiration",
        "maintenance"
    ],
    "NDEPLOY": [
        "growth",
        "new",
        "ndeploy",
        "total",
        "deployed"
    ],
    "NDEP_TO_SMINN": [
        "soil",
        "mineral",
        "ndep to sminn",
        "ndep_to_sminn",
        "deposition",
        "atmospheric"
    ],
    "NET_NMIN": [
        "net",
        "temp",
        "net_nmin",
        "mineralization",
        "net nmin",
        "temperature",
        "rate",
        "thermal"
    ],
    "OCDEP": [
        "ocdep",
        "deposition",
        "from",
        "dry",
        "wet",
        "total"
    ],
    "PCO2": [
        "atmospheric",
        "pco2",
        "partial",
        "pressure"
    ],
    "PFT_FIRE_CLOSS": [
        "loss",
        "temp",
        "patch",
        "total",
        "pft fire closs",
        "level",
        "temperature",
        "fire",
        "pft_fire_closs",
        "thermal"
    ],
    "PFT_FIRE_NLOSS": [
        "pft_fire_nloss",
        "loss",
        "temp",
        "patch",
        "total",
        "level",
        "temperature",
        "fire",
        "pft fire nloss",
        "thermal"
    ],
    "PLANT_NDEMAND": [
        "temp",
        "required",
        "initial",
        "support",
        "plant ndemand",
        "gpp",
        "temperature",
        "flux",
        "plant_ndemand",
        "thermal"
    ],
    "POTENTIAL_IMMOB": [
        "potential immob",
        "potential_immob",
        "potential",
        "immobilization"
    ],
    "PSNSHADE_TO_CPOOL": [
        "psnshade to cpool",
        "canopy",
        "from",
        "fixation",
        "psnshade_to_cpool",
        "shaded"
    ],
    "PSNSHA": [
        "photosynthesis",
        "shaded",
        "psnsha",
        "leaf"
    ],
    "PSNSUN": [
        "psnsun",
        "photosynthesis",
        "leaf",
        "sunlit"
    ],
    "PSNSUN_TO_CPOOL": [
        "canopy",
        "from",
        "fixation",
        "psnsun_to_cpool",
        "psnsun to cpool",
        "sunlit"
    ],
    "QDRIP": [
        "throughfall",
        "qdrip"
    ],
    "QFLX_ICE_DYNBAL": [
        "qflx ice dynbal",
        "ice",
        "dynamic",
        "qflx_ice_dynbal",
        "cover",
        "change",
        "land"
    ],
    "QFLX_LIQ_DYNBAL": [
        "dynamic",
        "liq",
        "qflx_liq_dynbal",
        "cover",
        "change",
        "qflx liq dynbal",
        "land"
    ],
    "QRUNOFF_RAIN_TO_SNOW_CONVERSION": [
        "precipitation",
        "rainfall",
        "qrunoff_rain_to_snow_conversion",
        "from",
        "snow",
        "qrunoff rain to snow conversion",
        "runoff",
        "liquid",
        "rain"
    ],
    "RETRANSN": [
        "retransn",
        "plant",
        "pool",
        "retranslocated"
    ],
    "RETRANSN_TO_NPOOL": [
        "retransn_to_npool",
        "retranslocated",
        "deployment",
        "retransn to npool"
    ],
    "RR": [
        "root",
        "total",
        "fine",
        "respiration"
    ],
    "SABG": [
        "sabg",
        "absorbed",
        "rad",
        "solar",
        "ground"
    ],
    "SABV": [
        "sabv",
        "absorbed",
        "rad",
        "solar",
        "veg"
    ],
    "SEEDC": [
        "new",
        "seeding",
        "pool",
        "seedc",
        "for",
        "pfts"
    ],
    "SEEDN": [
        "new",
        "seeding",
        "pool",
        "for",
        "pfts",
        "seedn"
    ],
    "SMINN": [
        "sminn",
        "soil",
        "mineral"
    ],
    "SMINN_TO_NPOOL": [
        "soil",
        "mineral",
        "sminn to npool",
        "deployment",
        "sminn_to_npool",
        "uptake"
    ],
    "SMINN_TO_PLANT": [
        "plant",
        "soil",
        "mineral",
        "sminn to plant",
        "sminn_to_plant",
        "uptake"
    ],
    "SNOBCMCL": [
        "column",
        "snow",
        "mass",
        "snobcmcl"
    ],
    "SNODSTMCL": [
        "dust",
        "mass",
        "snow",
        "snodstmcl",
        "column"
    ],
    "SNODSTMSL": [
        "layer",
        "top",
        "dust",
        "mass",
        "snow",
        "snodstmsl"
    ],
    "SNOOCMCL": [
        "snoocmcl",
        "column",
        "snow",
        "mass"
    ],
    "SNOOCMSL": [
        "layer",
        "top",
        "mass",
        "snoocmsl",
        "snow"
    ],
    "SNOW_SINKS": [
        "snow_sinks",
        "water",
        "snow",
        "liquid",
        "snow sinks",
        "sinks"
    ],
    "SOIL1C": [
        "soil1c"
    ],
    "SOIL1N": [
        "soil1n"
    ],
    "SOIL2C": [
        "soil2c"
    ],
    "SOIL2N": [
        "soil2n"
    ],
    "SOIL3C": [
        "soil3c"
    ],
    "SOIL3N": [
        "soil3n"
    ],
    "SR": [
        "root",
        "soil",
        "total",
        "respiration",
        "resp"
    ],
    "STORVEGC": [
        "carbon",
        "cpool",
        "vegetation",
        "excluding",
        "stored",
        "storvegc"
    ],
    "STORVEGN": [
        "storvegn",
        "nitrogen",
        "stored",
        "vegetation"
    ],
    "SUPPLEMENT_TO_SMINN": [
        "temp",
        "supplemental",
        "supply",
        "temperature",
        "supplement_to_sminn",
        "supplement to sminn",
        "thermal"
    ],
    "TBUILD": [
        "internal",
        "air",
        "building",
        "temperature",
        "urban",
        "tbuild"
    ],
    "THBOT": [
        "thbot",
        "downscaled",
        "atmospheric",
        "air",
        "temperature",
        "potential"
    ],
    "TOTCOLC": [
        "incl",
        "carbon",
        "totcolc",
        "total",
        "column",
        "veg"
    ],
    "TOTCOLN": [
        "total",
        "excluding",
        "level",
        "product",
        "column",
        "totcoln"
    ],
    "TOTLITC": [
        "total",
        "litter",
        "totlitc",
        "carbon"
    ],
    "TOTLITN": [
        "total",
        "totlitn",
        "litter"
    ],
    "TOTPFTC": [
        "carbon",
        "totpftc",
        "patch",
        "including",
        "total",
        "level"
    ],
    "TOTPFTN": [
        "totpftn",
        "patch",
        "nitrogen",
        "total",
        "level"
    ],
    "TOTSOMC": [
        "soil",
        "organic",
        "totsomc",
        "carbon",
        "total",
        "matter"
    ],
    "TOTSOMN": [
        "soil",
        "organic",
        "total",
        "matter",
        "totsomn"
    ],
    "TSAI": [
        "stem",
        "tsai",
        "total",
        "index",
        "area",
        "projected"
    ],
    "TSOI_ICE": [
        "ice",
        "soil",
        "only",
        "landunits",
        "temperature",
        "tsoi_ice",
        "tsoi ice"
    ],
    "URBAN_AC": [
        "air",
        "urban_ac",
        "urban",
        "flux",
        "conditioning",
        "urban ac"
    ],
    "URBAN_HEAT": [
        "heating",
        "urban heat",
        "urban_heat",
        "urban",
        "flux"
    ],
    "WASTEHEAT": [
        "heat",
        "from",
        "heating",
        "wasteheat",
        "sensible",
        "flux"
    ],
    "WOODC_ALLOC": [
        "woodc_alloc",
        "eallocation",
        "woodc alloc",
        "wood"
    ],
    "WOODC_LOSS": [
        "woodc loss",
        "wood",
        "loss",
        "woodc_loss"
    ],
    "WOODC": [
        "woodc",
        "wood"
    ],
    "WOOD_HARVESTC": [
        "pools",
        "carbon",
        "wood_harvestc",
        "product",
        "wood harvestc",
        "harvest",
        "wood"
    ],
    "WOOD_HARVESTN": [
        "pools",
        "wood harvestn",
        "wood_harvestn",
        "product",
        "harvest",
        "wood"
    ],
    "XSMRPOOL_RECOVER": [
        "xsmrpool recover",
        "assigned",
        "negative",
        "recovery",
        "xsmrpool_recover",
        "flux",
        "xsmrpool"
    ],
    "XSMRPOOL": [
        "temporary",
        "xsmrpool",
        "pool",
        "photosynthate"
    ],
    "ZBOT": [
        "atmospheric",
        "reference",
        "zbot",
        "height"
    ],
    "CPHASE": [
        "phenology",
        "cphase",
        "phase",
        "crop"
    ],
    "CROPPROD1C": [
        "product",
        "grain",
        "cropprod1c"
    ],
    "CWDC_vr": [
        "cwdc vr",
        "cwd",
        "vertically",
        "cwdc_vr",
        "resolved"
    ],
    "CWDN_vr": [
        "cwd",
        "cwdn_vr",
        "cwdn vr",
        "vertically",
        "resolved"
    ],
    "DEADCROOTC": [
        "deadcrootc",
        "root",
        "dead",
        "coarse"
    ],
    "FSNO_ICE": [
        "ice",
        "fsno_ice",
        "ground",
        "snow",
        "fsno ice",
        "covered",
        "fraction"
    ],
    "LITR1C_vr": [
        "litr1c_vr",
        "vertically",
        "litr1c vr",
        "resolved"
    ],
    "LITR1N_vr": [
        "vertically",
        "litr1n vr",
        "resolved",
        "litr1n_vr"
    ],
    "LITR2C_vr": [
        "litr2c vr",
        "vertically",
        "litr2c_vr",
        "resolved"
    ],
    "LITR2N_vr": [
        "litr2n vr",
        "vertically",
        "resolved",
        "litr2n_vr"
    ],
    "LITR3C_vr": [
        "vertically",
        "litr3c_vr",
        "resolved",
        "litr3c vr"
    ],
    "LITR3N_vr": [
        "vertically",
        "litr3n vr",
        "litr3n_vr",
        "resolved"
    ],
    "PCT_CFT": [
        "temp",
        "each",
        "pct_cft",
        "crop",
        "pct cft",
        "the",
        "temperature",
        "landunit",
        "thermal"
    ],
    "PCT_GLC_MEC": [
        "pct_glc_mec",
        "each",
        "temp",
        "elevation",
        "the",
        "temperature",
        "glc",
        "class",
        "pct glc mec",
        "thermal"
    ],
    "PCT_LANDUNIT": [
        "cell",
        "temp",
        "each",
        "grid",
        "temperature",
        "pct_landunit",
        "landunit",
        "pct landunit",
        "thermal"
    ],
    "PCT_NAT_PFT": [
        "temp",
        "each",
        "natural",
        "vegetation",
        "pft",
        "the",
        "temperature",
        "pct nat pft",
        "pct_nat_pft",
        "thermal"
    ],
    "QICE_FORC": [
        "qice forc",
        "qice_forc",
        "qice",
        "forcing",
        "sent",
        "glc"
    ],
    "SOIL1C_vr": [
        "vertically",
        "soil1c vr",
        "soil1c_vr",
        "resolved"
    ],
    "SOIL1N_vr": [
        "vertically",
        "soil1n vr",
        "soil1n_vr",
        "resolved"
    ],
    "SOIL2C_vr": [
        "vertically",
        "resolved",
        "soil2c_vr",
        "soil2c vr"
    ],
    "SOIL2N_vr": [
        "vertically",
        "soil2n vr",
        "resolved",
        "soil2n_vr"
    ],
    "SOIL3C_vr": [
        "vertically",
        "resolved",
        "soil3c vr",
        "soil3c_vr"
    ],
    "SOIL3N_vr": [
        "soil3n vr",
        "soil3n_vr",
        "vertically",
        "resolved"
    ],
    "TOPO_FORC": [
        "topo_forc",
        "topograephic",
        "topo forc",
        "sent",
        "glc",
        "height"
    ],
    "TOTECOSYSC": [
        "incl",
        "totecosysc",
        "carbon",
        "total",
        "ecosystem",
        "veg"
    ],
    "TOTSOMC_1m": [
        "soil",
        "organic",
        "totsomc_1m",
        "carbon",
        "totsomc 1m",
        "total",
        "matter"
    ],
    "TOTVEGC": [
        "carbon",
        "cpool",
        "vegetation",
        "total",
        "excluding",
        "totvegc"
    ],
    "TOT_WOODPRODC": [
        "temp",
        "total",
        "temperature",
        "product",
        "tot woodprodc",
        "tot_woodprodc",
        "wood",
        "thermal"
    ],
    "TSRF_FORC": [
        "tsrf_forc",
        "sent",
        "temperature",
        "glc",
        "surface",
        "tsrf forc"
    ],
    "ACTUAL_IMMOB": [
        "immobilization",
        "actual_immob",
        "actual",
        "actual immob"
    ],
    "AGNPP": [
        "npp",
        "agnpp",
        "aboveground"
    ],
    "ALTMAX": [
        "layer",
        "active",
        "maximum",
        "annual",
        "thickness",
        "altmax"
    ],
    "ATM_TOPO": [
        "atm_topo",
        "atmospheric",
        "atm topo",
        "surface",
        "height"
    ],
    "BAF_CROP": [
        "baf_crop",
        "burned",
        "fractional",
        "for",
        "crop",
        "area",
        "baf crop"
    ],
    "BAF_PEATF": [
        "burned",
        "fractional",
        "peatland",
        "baf_peatf",
        "area",
        "baf peatf"
    ],
    "BCDEP": [
        "deposition",
        "from",
        "dry",
        "wet",
        "total",
        "bcdep"
    ],
    "BGNPP": [
        "bgnpp",
        "npp",
        "belowground"
    ],
    "BTRAN2": [
        "root",
        "btran2",
        "soil",
        "factor",
        "wetness",
        "zone"
    ],
    "BTRANMN": [
        "daily",
        "btranmn",
        "minimum",
        "transpiration",
        "factor",
        "beta"
    ],
    "C13_AGNPP": [
        "c13_agnpp",
        "aboveground",
        "npp",
        "c13 agnpp"
    ],
    "C13_AR": [
        "c13 ar",
        "c13_ar",
        "autotrophic",
        "respiration"
    ],
    "C13_BGNPP": [
        "npp",
        "belowground",
        "c13 bgnpp",
        "c13_bgnpp"
    ],
    "C13_COL_FIRE_CLOSS": [
        "c13_col_fire_closs",
        "loss",
        "total",
        "level",
        "fire",
        "c13 col fire closs",
        "column"
    ],
    "C13_CPOOL": [
        "pool",
        "c13_cpool",
        "c13 cpool",
        "photosynthate",
        "temporary"
    ],
    "C13_CROPPROD1C_LOSS": [
        "pool",
        "loss",
        "from",
        "grain",
        "c13 cropprod1c loss",
        "c13_cropprod1c_loss",
        "product"
    ],
    "C13_CROPPROD1C": [
        "product",
        "c13_cropprod1c",
        "grain",
        "c13 cropprod1c"
    ],
    "C13_CROPSEEDC_DEFICIT": [
        "used",
        "c13_cropseedc_deficit",
        "that",
        "crop",
        "c13 cropseedc deficit",
        "for",
        "seed"
    ],
    "C13_CWDC": [
        "c13_cwdc",
        "cwd",
        "c13 cwdc"
    ],
    "C13_DEADCROOTC": [
        "root",
        "dead",
        "c13_deadcrootc",
        "c13 deadcrootc",
        "coarse"
    ],
    "C13_DEADSTEMC": [
        "c13 deadstemc",
        "dead",
        "c13_deadstemc",
        "stem"
    ],
    "C13_DISPVEGC": [
        "c13_dispvegc",
        "c13 dispvegc",
        "storage",
        "carbon",
        "displayed",
        "excluding",
        "veg"
    ],
    "C13_DWT_CONV_CFLUX_DRIBBLED": [
        "conversion",
        "loss",
        "atm",
        "temp",
        "c13 dwt conv cflux dribbled",
        "temperature",
        "flux",
        "immediate",
        "c13_dwt_conv_cflux_dribbled",
        "thermal"
    ],
    "C13_DWT_CONV_CFLUX": [
        "conversion",
        "immediate",
        "loss",
        "atm",
        "temp",
        "c13_dwt_conv_cflux",
        "temperature",
        "flux",
        "c13 dwt conv cflux",
        "thermal"
    ],
    "C13_DWT_CROPPROD1C_GAIN": [
        "temp",
        "addition",
        "c13_dwt_cropprod1c_gain",
        "c13 dwt cropprod1c gain",
        "year",
        "change",
        "temperature",
        "driven",
        "landcover",
        "thermal"
    ],
    "C13_DWT_SLASH_CFLUX": [
        "cwd",
        "temp",
        "c13 dwt slash cflux",
        "slash",
        "c13_dwt_slash_cflux",
        "and",
        "litter",
        "temperature",
        "flux",
        "thermal"
    ],
    "C13_DWT_WOODPRODC_GAIN": [
        "temp",
        "addition",
        "c13_dwt_woodprodc_gain",
        "change",
        "temperature",
        "driven",
        "landcover",
        "c13 dwt woodprodc gain",
        "wood",
        "thermal"
    ],
    "C13_ER": [
        "heterotrophic",
        "c13_er",
        "c13 er",
        "total",
        "respiration",
        "ecosystem",
        "autotrophic"
    ],
    "C13_FROOTC": [
        "root",
        "fine",
        "c13_frootc",
        "c13 frootc"
    ],
    "C13_GPP": [
        "c13 gpp",
        "gross",
        "primary",
        "production",
        "c13_gpp"
    ],
    "C13_GRAINC": [
        "precipitation",
        "rainfall",
        "does",
        "not",
        "grain",
        "c13_grainc",
        "equal",
        "c13 grainc",
        "yield",
        "rain"
    ],
    "C13_GR": [
        "growth",
        "total",
        "c13_gr",
        "respiration",
        "c13 gr"
    ],
    "C13_HR": [
        "heterotrophic",
        "total",
        "c13_hr",
        "respiration",
        "c13 hr"
    ],
    "C13_LEAFC": [
        "c13 leafc",
        "leaf",
        "c13_leafc"
    ],
    "C13_LITR1C": [
        "c13_litr1c",
        "c13 litr1c"
    ],
    "C13_LITR2C": [
        "c13_litr2c",
        "c13 litr2c"
    ],
    "C13_LITR3C": [
        "c13_litr3c",
        "c13 litr3c"
    ],
    "C13_LITTERC_HR": [
        "root",
        "fine",
        "c13 litterc hr",
        "c13_litterc_hr",
        "litter",
        "litterfall"
    ],
    "C13_LIVECROOTC": [
        "live",
        "root",
        "c13_livecrootc",
        "c13 livecrootc",
        "coarse"
    ],
    "C13_LIVESTEMC": [
        "live",
        "c13 livestemc",
        "c13_livestemc",
        "stem"
    ],
    "C13_MR": [
        "respiration",
        "maintenance",
        "c13 mr",
        "c13_mr"
    ],
    "C13_NEE": [
        "net",
        "c13 nee",
        "carbon",
        "includes",
        "c13_nee",
        "ecosystem",
        "exchange"
    ],
    "C13_NEP": [
        "net",
        "fire",
        "c13_nep",
        "c13 nep",
        "production",
        "ecosystem",
        "excludes"
    ],
    "C13_NPP": [
        "net",
        "c13_npp",
        "c13 npp",
        "primary",
        "production"
    ],
    "C13_PFT_FIRE_CLOSS": [
        "c13_pft_fire_closs",
        "loss",
        "temp",
        "patch",
        "total",
        "level",
        "temperature",
        "c13 pft fire closs",
        "fire",
        "thermal"
    ],
    "C13_PSNSHADE_TO_CPOOL": [
        "canopy",
        "from",
        "fixation",
        "c13_psnshade_to_cpool",
        "shaded",
        "c13 psnshade to cpool"
    ],
    "C13_PSNSHA": [
        "c13 psnsha",
        "photosynthesis",
        "c13_psnsha",
        "shaded",
        "leaf"
    ],
    "C13_PSNSUN": [
        "c13_psnsun",
        "photosynthesis",
        "sunlit",
        "c13 psnsun",
        "leaf"
    ],
    "C13_PSNSUN_TO_CPOOL": [
        "canopy",
        "from",
        "c13 psnsun to cpool",
        "fixation",
        "sunlit",
        "c13_psnsun_to_cpool"
    ],
    "C13_RR": [
        "root",
        "fine",
        "c13 rr",
        "total",
        "respiration",
        "c13_rr"
    ],
    "C13_SEEDC": [
        "new",
        "seeding",
        "pool",
        "for",
        "pfts",
        "c13 seedc",
        "c13_seedc"
    ],
    "C13_SOIL1C": [
        "c13 soil1c",
        "c13_soil1c"
    ],
    "C13_SOIL2C": [
        "c13_soil2c",
        "c13 soil2c"
    ],
    "C13_SOIL3C": [
        "c13_soil3c",
        "c13 soil3c"
    ],
    "C13_SOILC_HR": [
        "heterotrophic",
        "soil",
        "organic",
        "c13 soilc hr",
        "c13_soilc_hr",
        "matter",
        "respiration"
    ],
    "C13_SR": [
        "root",
        "soil",
        "c13 sr",
        "c13_sr",
        "total",
        "respiration",
        "resp"
    ],
    "C13_STORVEGC": [
        "carbon",
        "c13 storvegc",
        "cpool",
        "vegetation",
        "excluding",
        "stored",
        "c13_storvegc"
    ],
    "C13_TOTCOLC": [
        "incl",
        "carbon",
        "column",
        "total",
        "c13 totcolc",
        "c13_totcolc",
        "veg"
    ],
    "C13_TOTECOSYSC": [
        "c13_totecosysc",
        "incl",
        "carbon",
        "c13 totecosysc",
        "total",
        "ecosystem",
        "veg"
    ],
    "C13_TOTLITC_1m": [
        "carbon",
        "total",
        "meter",
        "litter",
        "c13_totlitc_1m",
        "c13 totlitc 1m"
    ],
    "C13_TOTLITC": [
        "carbon",
        "c13 totlitc",
        "c13_totlitc",
        "total",
        "litter"
    ],
    "C13_TOTPFTC": [
        "carbon",
        "patch",
        "including",
        "total",
        "c13_totpftc",
        "level",
        "c13 totpftc"
    ],
    "C13_TOTSOMC_1m": [
        "soil",
        "organic",
        "carbon",
        "c13_totsomc_1m",
        "total",
        "matter",
        "c13 totsomc 1m"
    ],
    "C13_TOTSOMC": [
        "soil",
        "organic",
        "carbon",
        "c13_totsomc",
        "c13 totsomc",
        "total",
        "matter"
    ],
    "C13_TOTVEGC": [
        "carbon",
        "c13 totvegc",
        "cpool",
        "vegetation",
        "total",
        "excluding",
        "c13_totvegc"
    ],
    "C13_TOT_WOODPRODC_LOSS": [
        "loss",
        "temp",
        "c13 tot woodprodc loss",
        "from",
        "total",
        "temperature",
        "product",
        "c13_tot_woodprodc_loss",
        "wood",
        "thermal"
    ],
    "C13_TOT_WOODPRODC": [
        "temp",
        "c13 tot woodprodc",
        "c13_tot_woodprodc",
        "total",
        "temperature",
        "product",
        "wood",
        "thermal"
    ],
    "C13_XSMRPOOL": [
        "pool",
        "c13_xsmrpool",
        "photosynthate",
        "temporary",
        "c13 xsmrpool"
    ],
    "C14_AGNPP": [
        "npp",
        "aboveground",
        "c14 agnpp",
        "c14_agnpp"
    ],
    "C14_AR": [
        "c14_ar",
        "autotrophic",
        "c14 ar",
        "respiration"
    ],
    "C14_BGNPP": [
        "npp",
        "c14 bgnpp",
        "belowground",
        "c14_bgnpp"
    ],
    "C14_COL_FIRE_CLOSS": [
        "c14 col fire closs",
        "c14_col_fire_closs",
        "loss",
        "total",
        "level",
        "fire",
        "column"
    ],
    "C14_CPOOL": [
        "pool",
        "c14 cpool",
        "c14_cpool",
        "photosynthate",
        "temporary"
    ],
    "C14_CROPPROD1C_LOSS": [
        "pool",
        "loss",
        "c14_cropprod1c_loss",
        "from",
        "grain",
        "c14 cropprod1c loss",
        "product"
    ],
    "C14_CROPPROD1C": [
        "product",
        "c14_cropprod1c",
        "c14 cropprod1c",
        "grain"
    ],
    "C14_CROPSEEDC_DEFICIT": [
        "used",
        "that",
        "c14_cropseedc_deficit",
        "crop",
        "for",
        "seed",
        "c14 cropseedc deficit"
    ],
    "C14_CWDC": [
        "c14 cwdc",
        "cwd",
        "c14_cwdc"
    ],
    "C14_DEADCROOTC": [
        "root",
        "dead",
        "c14 deadcrootc",
        "c14_deadcrootc",
        "coarse"
    ],
    "C14_DEADSTEMC": [
        "dead",
        "c14 deadstemc",
        "c14_deadstemc",
        "stem"
    ],
    "C14_DISPVEGC": [
        "storage",
        "c14_dispvegc",
        "carbon",
        "displayed",
        "excluding",
        "c14 dispvegc",
        "veg"
    ],
    "C14_DWT_CONV_CFLUX_DRIBBLED": [
        "conversion",
        "loss",
        "atm",
        "temp",
        "c14_dwt_conv_cflux_dribbled",
        "temperature",
        "c14 dwt conv cflux dribbled",
        "flux",
        "immediate",
        "thermal"
    ],
    "C14_DWT_CONV_CFLUX": [
        "conversion",
        "loss",
        "atm",
        "temp",
        "c14 dwt conv cflux",
        "c14_dwt_conv_cflux",
        "temperature",
        "flux",
        "immediate",
        "thermal"
    ],
    "C14_DWT_CROPPROD1C_GAIN": [
        "temp",
        "addition",
        "c14 dwt cropprod1c gain",
        "year",
        "change",
        "temperature",
        "driven",
        "landcover",
        "c14_dwt_cropprod1c_gain",
        "thermal"
    ],
    "C14_DWT_SLASH_CFLUX": [
        "c14_dwt_slash_cflux",
        "cwd",
        "temp",
        "slash",
        "and",
        "litter",
        "temperature",
        "c14 dwt slash cflux",
        "flux",
        "thermal"
    ],
    "C14_DWT_WOODPRODC_GAIN": [
        "temp",
        "addition",
        "c14 dwt woodprodc gain",
        "change",
        "c14_dwt_woodprodc_gain",
        "landcover",
        "driven",
        "temperature",
        "wood",
        "thermal"
    ],
    "C14_ER": [
        "heterotrophic",
        "autotrophic",
        "total",
        "respiration",
        "ecosystem",
        "c14 er",
        "c14_er"
    ],
    "C14_FROOTC": [
        "root",
        "fine",
        "c14 frootc",
        "c14_frootc"
    ],
    "C14_GPP": [
        "c14 gpp",
        "gross",
        "c14_gpp",
        "primary",
        "production"
    ],
    "C14_GRAINC": [
        "c14 grainc",
        "precipitation",
        "rainfall",
        "does",
        "not",
        "grain",
        "equal",
        "c14_grainc",
        "yield",
        "rain"
    ],
    "C14_GR": [
        "growth",
        "c14 gr",
        "c14_gr",
        "total",
        "respiration"
    ],
    "C14_HR": [
        "heterotrophic",
        "c14 hr",
        "c14_hr",
        "total",
        "respiration"
    ],
    "C14_LEAFC": [
        "c14 leafc",
        "c14_leafc",
        "leaf"
    ],
    "C14_LITR1C": [
        "c14 litr1c",
        "c14_litr1c"
    ],
    "C14_LITR2C": [
        "c14_litr2c",
        "c14 litr2c"
    ],
    "C14_LITR3C": [
        "c14_litr3c",
        "c14 litr3c"
    ],
    "C14_LITTERC_HR": [
        "c14 litterc hr",
        "heterotrophic",
        "carbon",
        "c14_litterc_hr",
        "respiration",
        "litter"
    ],
    "C14_LIVECROOTC": [
        "live",
        "root",
        "c14 livecrootc",
        "coarse",
        "c14_livecrootc"
    ],
    "C14_LIVESTEMC": [
        "live",
        "c14 livestemc",
        "c14_livestemc",
        "stem"
    ],
    "C14_MR": [
        "c14 mr",
        "respiration",
        "maintenance",
        "c14_mr"
    ],
    "C14_NEE": [
        "net",
        "c14_nee",
        "carbon",
        "includes",
        "c14 nee",
        "ecosystem",
        "exchange"
    ],
    "C14_NEP": [
        "net",
        "fire",
        "excludes",
        "c14_nep",
        "production",
        "ecosystem",
        "c14 nep"
    ],
    "C14_NPP": [
        "net",
        "c14_npp",
        "primary",
        "production",
        "c14 npp"
    ],
    "C14_PFT_CTRUNC": [
        "temp",
        "c14 pft ctrunc",
        "c14_pft_ctrunc",
        "patch",
        "for",
        "level",
        "temperature",
        "sink",
        "truncation",
        "thermal"
    ],
    "C14_PFT_FIRE_CLOSS": [
        "loss",
        "c14_pft_fire_closs",
        "temp",
        "patch",
        "c14 pft fire closs",
        "total",
        "level",
        "temperature",
        "fire",
        "thermal"
    ],
    "C14_PSNSHADE_TO_CPOOL": [
        "canopy",
        "from",
        "fixation",
        "c14 psnshade to cpool",
        "shaded",
        "c14_psnshade_to_cpool"
    ],
    "C14_PSNSHA": [
        "shaded",
        "photosynthesis",
        "c14_psnsha",
        "c14 psnsha",
        "leaf"
    ],
    "C14_PSNSUN": [
        "c14 psnsun",
        "photosynthesis",
        "sunlit",
        "leaf",
        "c14_psnsun"
    ],
    "C14_PSNSUN_TO_CPOOL": [
        "canopy",
        "from",
        "c14 psnsun to cpool",
        "fixation",
        "c14_psnsun_to_cpool",
        "sunlit"
    ],
    "C14_RR": [
        "c14 rr",
        "root",
        "fine",
        "c14_rr",
        "total",
        "respiration"
    ],
    "C14_SEEDC": [
        "new",
        "seeding",
        "pool",
        "for",
        "pfts",
        "c14 seedc",
        "c14_seedc"
    ],
    "C14_SOIL1C": [
        "c14 soil1c",
        "c14_soil1c"
    ],
    "C14_SOIL2C": [
        "c14_soil2c",
        "c14 soil2c"
    ],
    "C14_SOIL3C": [
        "c14 soil3c",
        "c14_soil3c"
    ],
    "C14_SOILC_HR": [
        "heterotrophic",
        "soil",
        "organic",
        "c14 soilc hr",
        "matter",
        "respiration",
        "c14_soilc_hr"
    ],
    "C14_SR": [
        "root",
        "soil",
        "c14_sr",
        "total",
        "respiration",
        "resp",
        "c14 sr"
    ],
    "C14_STORVEGC": [
        "carbon",
        "c14 storvegc",
        "cpool",
        "vegetation",
        "excluding",
        "stored",
        "c14_storvegc"
    ],
    "C14_TOTCOLC": [
        "c14_totcolc",
        "incl",
        "carbon",
        "total",
        "c14 totcolc",
        "column",
        "veg"
    ],
    "C14_TOTECOSYSC": [
        "incl",
        "carbon",
        "c14 totecosysc",
        "total",
        "c14_totecosysc",
        "ecosystem",
        "veg"
    ],
    "C14_TOTLITC_1m": [
        "carbon",
        "total",
        "c14 totlitc 1m",
        "meter",
        "c14_totlitc_1m",
        "litter"
    ],
    "C14_TOTLITC": [
        "carbon",
        "c14_totlitc",
        "c14 totlitc",
        "total",
        "litter"
    ],
    "C14_TOTPFTC": [
        "carbon",
        "c14 totpftc",
        "patch",
        "including",
        "total",
        "level",
        "c14_totpftc"
    ],
    "C14_TOTSOMC_1m": [
        "soil",
        "organic",
        "carbon",
        "c14 totsomc 1m",
        "total",
        "matter",
        "c14_totsomc_1m"
    ],
    "C14_TOTSOMC": [
        "soil",
        "organic",
        "carbon",
        "c14 totsomc",
        "total",
        "matter",
        "c14_totsomc"
    ],
    "C14_TOTVEGC": [
        "carbon",
        "c14_totvegc",
        "cpool",
        "vegetation",
        "total",
        "excluding",
        "c14 totvegc"
    ],
    "C14_TOT_WOODPRODC_LOSS": [
        "loss",
        "temp",
        "from",
        "c14_tot_woodprodc_loss",
        "total",
        "c14 tot woodprodc loss",
        "temperature",
        "product",
        "wood",
        "thermal"
    ],
    "C14_TOT_WOODPRODC": [
        "temp",
        "c14 tot woodprodc",
        "total",
        "c14_tot_woodprodc",
        "temperature",
        "product",
        "wood",
        "thermal"
    ],
    "C14_XSMRPOOL": [
        "pool",
        "c14_xsmrpool",
        "c14 xsmrpool",
        "photosynthate",
        "temporary"
    ],
    "CH4PROD": [
        "total",
        "ch4prod",
        "production",
        "gridcell"
    ],
    "CH4_SURF_AERE_SAT": [
        "surface",
        "for",
        "ch4 surf aere sat",
        "inundated",
        "flux",
        "ch4_surf_aere_sat",
        "aerenchyma"
    ],
    "CH4_SURF_AERE_UNSAT": [
        "non",
        "for",
        "ch4 surf aere unsat",
        "ch4_surf_aere_unsat",
        "flux",
        "surface",
        "aerenchyma"
    ],
    "CH4_SURF_DIFF_SAT": [
        "diffusive",
        "for",
        "ch4 surf diff sat",
        "ch4_surf_diff_sat",
        "inundated",
        "flux",
        "surface"
    ],
    "CH4_SURF_DIFF_UNSAT": [
        "diffusive",
        "non",
        "ch4 surf diff unsat",
        "ch4_surf_diff_unsat",
        "for",
        "flux",
        "surface"
    ],
    "CH4_SURF_EBUL_SAT": [
        "ch4 surf ebul sat",
        "ebullition",
        "for",
        "ch4_surf_ebul_sat",
        "inundated",
        "flux",
        "surface"
    ],
    "CH4_SURF_EBUL_UNSAT": [
        "non",
        "ebullition",
        "for",
        "ch4 surf ebul unsat",
        "flux",
        "surface",
        "ch4_surf_ebul_unsat"
    ],
    "COL_FIRE_CLOSS": [
        "col fire closs",
        "loss",
        "total",
        "level",
        "fire",
        "column",
        "col_fire_closs"
    ],
    "COL_FIRE_NLOSS": [
        "loss",
        "col fire nloss",
        "total",
        "col_fire_nloss",
        "level",
        "fire",
        "column"
    ],
    "COST_NACTIVE": [
        "active",
        "cost nactive",
        "temp",
        "cost",
        "cost_nactive",
        "temperature",
        "uptake",
        "thermal"
    ],
    "COST_NFIX": [
        "temp",
        "cost",
        "fixation",
        "temperature",
        "thermal",
        "cost_nfix",
        "cost nfix"
    ],
    "COST_NRETRANS": [
        "temp",
        "cost",
        "cost_nretrans",
        "retranslocation",
        "temperature",
        "cost nretrans",
        "thermal"
    ],
    "CPOOL": [
        "temporary",
        "pool",
        "cpool",
        "photosynthate"
    ],
    "CROPPROD1C_LOSS": [
        "pool",
        "loss",
        "from",
        "grain",
        "cropprod1c_loss",
        "cropprod1c loss",
        "product"
    ],
    "CROPPROD1N_LOSS": [
        "cropprod1n_loss",
        "pool",
        "loss",
        "from",
        "grain",
        "cropprod1n loss",
        "product"
    ],
    "CROPPROD1N": [
        "product",
        "grain",
        "cropprod1n"
    ],
    "CROPSEEDC_DEFICIT": [
        "used",
        "that",
        "cropseedc_deficit",
        "crop",
        "for",
        "seed",
        "cropseedc deficit"
    ],
    "CWDC_LOSS": [
        "loss",
        "cwdc_loss",
        "woody",
        "cwdc loss",
        "debris",
        "coarse"
    ],
    "CWDC": [
        "cwd",
        "cwdc"
    ],
    "CWDN": [
        "cwd",
        "cwdn"
    ],
    "DEADCROOTN": [
        "coarse",
        "root",
        "deadcrootn",
        "dead"
    ],
    "DEADSTEMC": [
        "dead",
        "stem",
        "deadstemc"
    ],
    "DEADSTEMN": [
        "deadstemn",
        "dead",
        "stem"
    ],
    "DENIT": [
        "total",
        "denitrification",
        "denit",
        "rate"
    ],
    "DISPVEGC": [
        "dispvegc",
        "storage",
        "carbon",
        "displayed",
        "excluding",
        "veg"
    ],
    "DISPVEGN": [
        "dispvegn",
        "vegetation",
        "nitrogen",
        "displayed"
    ],
    "DSL": [
        "layer",
        "dry",
        "dsl",
        "surface",
        "thickness"
    ],
    "DSTDEP": [
        "dust",
        "deposition",
        "dry",
        "wet",
        "total",
        "dstdep"
    ],
    "DSTFLXT": [
        "dust",
        "emission",
        "total",
        "dstflxt",
        "surface"
    ],
    "DWT_CONV_CFLUX_DRIBBLED": [
        "conversion",
        "dwt conv cflux dribbled",
        "loss",
        "atm",
        "temp",
        "dwt_conv_cflux_dribbled",
        "temperature",
        "flux",
        "immediate",
        "thermal"
    ],
    "DWT_CONV_CFLUX_PATCH": [
        "dwt_conv_cflux_patch",
        "conversion",
        "temp",
        "patch",
        "dwt conv cflux patch",
        "level",
        "temperature",
        "flux",
        "immediate",
        "thermal"
    ],
    "DWT_CONV_CFLUX": [
        "conversion",
        "loss",
        "atm",
        "temp",
        "dwt conv cflux",
        "temperature",
        "dwt_conv_cflux",
        "flux",
        "immediate",
        "thermal"
    ],
    "DWT_CONV_NFLUX": [
        "dwt conv nflux",
        "conversion",
        "loss",
        "atm",
        "temp",
        "temperature",
        "dwt_conv_nflux",
        "flux",
        "immediate",
        "thermal"
    ],
    "DWT_CROPPROD1C_GAIN": [
        "dwt_cropprod1c_gain",
        "dwt cropprod1c gain",
        "temp",
        "addition",
        "year",
        "change",
        "temperature",
        "driven",
        "landcover",
        "thermal"
    ],
    "DWT_CROPPROD1N_GAIN": [
        "temp",
        "addition",
        "year",
        "dwt_cropprod1n_gain",
        "change",
        "dwt cropprod1n gain",
        "temperature",
        "driven",
        "landcover",
        "thermal"
    ],
    "DWT_SLASH_CFLUX": [
        "cwd",
        "temp",
        "dwt_slash_cflux",
        "slash",
        "dwt slash cflux",
        "and",
        "litter",
        "temperature",
        "flux",
        "thermal"
    ],
    "DWT_WOODPRODC_GAIN": [
        "dwt_woodprodc_gain",
        "temp",
        "dwt woodprodc gain",
        "addition",
        "change",
        "temperature",
        "landcover",
        "driven",
        "wood",
        "thermal"
    ],
    "DWT_WOODPRODN_GAIN": [
        "temp",
        "dwt woodprodn gain",
        "addition",
        "change",
        "dwt_woodprodn_gain",
        "temperature",
        "landcover",
        "driven",
        "wood",
        "thermal"
    ],
    "DWT_WOOD_PRODUCTC_GAIN_PATCH": [
        "temp",
        "dwt wood productc gain patch",
        "patch",
        "dwt_wood_productc_gain_patch",
        "level",
        "change",
        "temperature",
        "landcover",
        "driven",
        "thermal"
    ],
    "EFLXBUILD": [
        "heat",
        "from",
        "eflxbuild",
        "building",
        "change",
        "flux"
    ],
    "EFLX_GRND_LAKE": [
        "net",
        "heat",
        "eflx_grnd_lake",
        "lake",
        "eflx grnd lake",
        "flux",
        "into"
    ],
    "EFLX_LH_TOT_ICE": [
        "latent",
        "heat",
        "temp",
        "atm",
        "total",
        "eflx_lh_tot_ice",
        "temperature",
        "flux",
        "thermal",
        "eflx lh tot ice"
    ],
    "ELAI": [
        "one",
        "elai",
        "exposed",
        "area",
        "sided",
        "leaf"
    ],
    "ERRH2O": [
        "water",
        "errh2o",
        "total",
        "error",
        "conservation"
    ],
    "ER": [
        "heterotrophic",
        "total",
        "respiration",
        "ecosystem",
        "autotrophic"
    ],
    "FAREA_BURNED": [
        "burned",
        "farea burned",
        "farea_burned",
        "fractional",
        "area",
        "timestep"
    ],
    "FCEV": [
        "fcev",
        "evaporation",
        "canopy"
    ],
    "FCH4_DFSAT": [
        "fch4 dfsat",
        "changing",
        "additional",
        "fsat",
        "due",
        "fch4_dfsat",
        "flux"
    ],
    "FCH4": [
        "atm",
        "fch4",
        "atmosphere",
        "gridcell",
        "flux",
        "surface"
    ],
    "FCH4TOCO2": [
        "fch4toco2",
        "oxidation",
        "gridcell"
    ],
    "FCTR": [
        "fctr",
        "transpiration",
        "canopy"
    ],
    "F_DENIT": [
        "f_denit",
        "flux",
        "f denit",
        "denitrification"
    ],
    "FGEV": [
        "fgev",
        "ground",
        "evaporation"
    ],
    "FH2OSFC": [
        "fh2osfc",
        "water",
        "ground",
        "covered",
        "fraction",
        "surface"
    ],
    "FINUNDATED": [
        "columns",
        "vegetated",
        "finundated",
        "fractional",
        "area",
        "inundated"
    ],
    "FIRE_ICE": [
        "fire ice",
        "ice",
        "infrared",
        "longwave",
        "radiation",
        "fire_ice",
        "emitted"
    ],
    "FIRE_R": [
        "rural",
        "infrared",
        "longwave",
        "fire r",
        "radiation",
        "fire_r",
        "emitted"
    ],
    "FIRE": [
        "infrared",
        "longwave",
        "radiation",
        "fire",
        "emitted"
    ],
    "FLDS_ICE": [
        "flds ice",
        "columns",
        "downscaled",
        "atmospheric",
        "longwave",
        "radiation",
        "flds_ice"
    ],
    "F_N2O_DENIT": [
        "f_n2o_denit",
        "denitrification",
        "flux",
        "f n2o denit"
    ],
    "F_N2O_NIT": [
        "f_n2o_nit",
        "flux",
        "nitrification",
        "f n2o nit"
    ],
    "F_NIT": [
        "nitrification",
        "flux",
        "f nit",
        "f_nit"
    ],
    "FPSN": [
        "photosynthesis",
        "fpsn"
    ],
    "FREE_RETRANSN_TO_NPOOL": [
        "free retransn to npool",
        "retranslocated",
        "free_retransn_to_npool",
        "deployment"
    ],
    "FROOTC_TO_LITTER": [
        "root",
        "fine",
        "frootc to litter",
        "litterfall",
        "frootc_to_litter"
    ],
    "FSDSVILN": [
        "diffuse",
        "radiation",
        "solar",
        "fsdsviln",
        "vis",
        "incident"
    ],
    "FSH_ICE": [
        "fsh ice",
        "heat",
        "correction",
        "not",
        "including",
        "fsh_ice",
        "sensible"
    ],
    "FSH_PRECIP_CONVERSION": [
        "precipitation",
        "heat",
        "fsh precip conversion",
        "conversion",
        "rainfall",
        "from",
        "fsh_precip_conversion",
        "sensible",
        "flux",
        "rain"
    ],
    "FSH_RUNOFF_ICE_TO_LIQ": [
        "heat",
        "fsh_runoff_ice_to_liq",
        "from",
        "fsh runoff ice to liq",
        "generated",
        "sensible",
        "flux"
    ],
    "FSH_TO_COUPLER": [
        "heat",
        "coupler",
        "includes",
        "fsh to coupler",
        "sent",
        "fsh_to_coupler",
        "sensible"
    ],
    "FSNO_EFF": [
        "effective",
        "ground",
        "snow",
        "covered",
        "fraction",
        "fsno_eff",
        "fsno eff"
    ],
    "FSR_ICE": [
        "fsr_ice",
        "ice",
        "landunits",
        "fsr ice",
        "radiation",
        "solar",
        "reflected"
    ],
    "FSRND": [
        "nir",
        "radiation",
        "solar",
        "fsrnd",
        "direct",
        "reflected"
    ],
    "FSRNI": [
        "nir",
        "diffuse",
        "radiation",
        "solar",
        "reflected",
        "fsrni"
    ],
    "FSR": [
        "solar",
        "radiation",
        "fsr",
        "reflected"
    ],
    "FSRVD": [
        "radiation",
        "solar",
        "vis",
        "direct",
        "reflected",
        "fsrvd"
    ],
    "FSRVI": [
        "diffuse",
        "radiation",
        "solar",
        "vis",
        "reflected",
        "fsrvi"
    ],
    "FUELC": [
        "load",
        "fuel",
        "fuelc"
    ],
    "GRAINC": [
        "precipitation",
        "rainfall",
        "does",
        "grainc",
        "not",
        "grain",
        "equal",
        "yield",
        "rain"
    ],
    "GRAINC_TO_FOOD": [
        "grainc to food",
        "precipitation",
        "rainfall",
        "grain",
        "food",
        "rain",
        "grainc_to_food"
    ],
    "GRAINC_TO_SEED": [
        "precipitation",
        "rainfall",
        "grain",
        "grainc to seed",
        "seed",
        "grainc_to_seed",
        "rain"
    ],
    "GRAINN": [
        "precipitation",
        "rainfall",
        "grain",
        "rain",
        "grainn"
    ],
    "GSSHALN": [
        "stomatal",
        "conductance",
        "local",
        "shaded",
        "gsshaln",
        "leaf"
    ],
    "GSSHA": [
        "stomatal",
        "conductance",
        "gssha",
        "shaded",
        "leaf"
    ],
    "GSSUNLN": [
        "stomatal",
        "conductance",
        "local",
        "sunlit",
        "gssunln",
        "leaf"
    ],
    "GSSUN": [
        "conductance",
        "stomatal",
        "sunlit",
        "leaf",
        "gssun"
    ],
    "HEAT_CONTENT1": [
        "heat content1",
        "heat",
        "temp",
        "initial",
        "content",
        "heat_content1",
        "gridcell",
        "total",
        "temperature",
        "thermal"
    ],
    "HIA_R": [
        "rural",
        "heat",
        "nws",
        "index",
        "hia r",
        "hia_r"
    ],
    "HIA": [
        "hia",
        "index",
        "nws",
        "heat"
    ],
    "HIA_U": [
        "heat",
        "nws",
        "hia_u",
        "index",
        "urban",
        "hia u"
    ],
    "HR_vr": [
        "heterotrophic",
        "hr vr",
        "total",
        "vertically",
        "respiration",
        "hr_vr",
        "resolved"
    ],
    "HUMIDEX_R": [
        "humidex r",
        "rural",
        "humidex_r",
        "humidex"
    ],
    "HUMIDEX": [
        "humidex"
    ],
    "HUMIDEX_U": [
        "humidex u",
        "humidex",
        "urban",
        "humidex_u"
    ],
    "ICE_CONTENT1": [
        "ice",
        "initial",
        "content",
        "gridcell",
        "total",
        "ice_content1",
        "ice content1"
    ],
    "JMX25T": [
        "profile",
        "jmx25t",
        "jmax",
        "canopy"
    ],
    "Jmx25Z": [
        "canopy",
        "jmx25z",
        "predicted",
        "model",
        "profile",
        "luna"
    ],
    "LAKEICEFRAC_SURF": [
        "layer",
        "ice",
        "mass",
        "lake",
        "lakeicefrac surf",
        "surface",
        "lakeicefrac_surf"
    ],
    "LAKEICETHICK": [
        "ice",
        "including",
        "lake",
        "lakeicethick",
        "physical",
        "thickness"
    ],
    "LEAFC_CHANGE": [
        "leafc_change",
        "change",
        "leaf",
        "leafc change"
    ],
    "LEAFCN": [
        "used",
        "flexible",
        "for",
        "leafcn",
        "ratio",
        "leaf"
    ],
    "LEAFC_TO_LITTER_FUN": [
        "used",
        "leafc to litter fun",
        "leafc_to_litter_fun",
        "litterfall",
        "fun",
        "leaf"
    ],
    "LEAFC_TO_LITTER": [
        "leafc to litter",
        "leafc_to_litter",
        "leaf",
        "litterfall"
    ],
    "LEAF_MR": [
        "respiration",
        "maintenance",
        "leaf_mr",
        "leaf mr",
        "leaf"
    ],
    "LEAFN_TO_LITTER": [
        "leafn_to_litter",
        "leafn to litter",
        "leaf",
        "litterfall"
    ],
    "LFC2": [
        "conversion",
        "lfc2",
        "bet",
        "and",
        "area",
        "fraction"
    ],
    "LIQCAN": [
        "water",
        "liqcan",
        "liquid",
        "intercepted"
    ],
    "LIQUID_CONTENT1": [
        "initial",
        "content",
        "gridcell",
        "total",
        "liq",
        "liquid_content1",
        "liquid content1"
    ],
    "LITR1N_TO_SOIL1N": [
        "soil",
        "litr1n to soil1n",
        "decomp",
        "litr1n_to_soil1n",
        "litter"
    ],
    "LITR2C_TO_SOIL1C": [
        "soil",
        "decomp",
        "litter",
        "litr2c to soil1c",
        "litr2c_to_soil1c"
    ],
    "LITR2N_TO_SOIL1N": [
        "soil",
        "decomp",
        "litr2n_to_soil1n",
        "litter",
        "litr2n to soil1n"
    ],
    "LITR3C_TO_SOIL2C": [
        "soil",
        "litr3c to soil2c",
        "litr3c_to_soil2c",
        "decomp",
        "litter"
    ],
    "LITR3N_TO_SOIL2N": [
        "litr3n to soil2n",
        "soil",
        "decomp",
        "litr3n_to_soil2n",
        "litter"
    ],
    "LITTERC_HR": [
        "litterc hr",
        "heterotrophic",
        "respiration",
        "litter",
        "litterc_hr"
    ],
    "LNC": [
        "concentration",
        "lnc",
        "leaf"
    ],
    "NACTIVE_NH4": [
        "nactive nh4",
        "nactive_nh4",
        "mycorrhizal",
        "flux",
        "uptake"
    ],
    "NACTIVE_NO3": [
        "mycorrhizal",
        "nactive no3",
        "flux",
        "uptake",
        "nactive_no3"
    ],
    "NACTIVE": [
        "mycorrhizal",
        "uptake",
        "nactive",
        "flux"
    ],
    "NAM_NH4": [
        "nam_nh4",
        "nam nh4",
        "associated",
        "flux",
        "uptake"
    ],
    "NAM_NO3": [
        "nam no3",
        "nam_no3",
        "flux",
        "associated",
        "uptake"
    ],
    "NAM": [
        "flux",
        "associated",
        "nam",
        "uptake"
    ],
    "NBP": [
        "net",
        "nbp",
        "includes",
        "production",
        "fire",
        "biome"
    ],
    "NECM_NH4": [
        "necm nh4",
        "ecm",
        "necm_nh4",
        "flux",
        "associated",
        "uptake"
    ],
    "NECM_NO3": [
        "ecm",
        "associated",
        "flux",
        "necm no3",
        "uptake",
        "necm_no3"
    ],
    "NECM": [
        "ecm",
        "necm",
        "associated",
        "flux",
        "uptake"
    ],
    "NEE": [
        "net",
        "carbon",
        "includes",
        "nee",
        "ecosystem",
        "exchange"
    ],
    "NEM": [
        "net",
        "adjustment",
        "nem",
        "carbon",
        "gridcell"
    ],
    "NEP": [
        "net",
        "fire",
        "production",
        "ecosystem",
        "excludes",
        "nep"
    ],
    "NFERTILIZATION": [
        "nfertilization",
        "fertilizer",
        "added"
    ],
    "NFIRE": [
        "reg",
        "only",
        "counts",
        "nfire",
        "fire",
        "valid"
    ],
    "NFIX": [
        "nfix",
        "symbiotic",
        "bnf",
        "flux",
        "uptake"
    ],
    "NNONMYC_NH4": [
        "non",
        "nnonmyc_nh4",
        "mycorrhizal",
        "flux",
        "nnonmyc nh4",
        "uptake"
    ],
    "NNONMYC_NO3": [
        "nnonmyc_no3",
        "non",
        "mycorrhizal",
        "flux",
        "uptake",
        "nnonmyc no3"
    ],
    "NNONMYC": [
        "non",
        "mycorrhizal",
        "flux",
        "nnonmyc",
        "uptake"
    ],
    "NPASSIVE": [
        "flux",
        "passive",
        "npassive",
        "uptake"
    ],
    "NPOOL": [
        "npool",
        "plant",
        "pool",
        "temporary"
    ],
    "NPP_GROWTH": [
        "growth",
        "npp growth",
        "used",
        "for",
        "total",
        "npp_growth",
        "fun"
    ],
    "NPP_NACTIVE_NH4": [
        "use",
        "mycorrhizal",
        "npp_nactive_nh4",
        "npp nactive nh4",
        "uptake"
    ],
    "NPP_NACTIVE_NO3": [
        "npp nactive no3",
        "used",
        "mycorrhizal",
        "npp_nactive_no3",
        "uptake"
    ],
    "NPP_NACTIVE": [
        "npp nactive",
        "used",
        "npp_nactive",
        "mycorrhizal",
        "uptake"
    ],
    "NPP_NAM_NH4": [
        "use",
        "npp nam nh4",
        "npp_nam_nh4",
        "associated",
        "uptake"
    ],
    "NPP_NAM_NO3": [
        "use",
        "npp_nam_no3",
        "associated",
        "uptake",
        "npp nam no3"
    ],
    "NPP_NAM": [
        "used",
        "npp nam",
        "npp_nam",
        "associated",
        "uptake"
    ],
    "NPP_NECM_NH4": [
        "use",
        "ecm",
        "npp necm nh4",
        "npp_necm_nh4",
        "associated",
        "uptake"
    ],
    "NPP_NECM_NO3": [
        "used",
        "npp_necm_no3",
        "ecm",
        "npp necm no3",
        "associated",
        "uptake"
    ],
    "NPP_NECM": [
        "used",
        "npp necm",
        "npp_necm",
        "ecm",
        "associated",
        "uptake"
    ],
    "NPP_NFIX": [
        "npp nfix",
        "used",
        "symbiotic",
        "npp_nfix",
        "bnf",
        "uptake"
    ],
    "NPP_NNONMYC_NH4": [
        "npp_nnonmyc_nh4",
        "non",
        "use",
        "mycorrhizal",
        "npp nnonmyc nh4",
        "uptake"
    ],
    "NPP_NNONMYC_NO3": [
        "non",
        "use",
        "mycorrhizal",
        "npp nnonmyc no3",
        "npp_nnonmyc_no3",
        "uptake"
    ],
    "NPP_NNONMYC": [
        "npp nnonmyc",
        "used",
        "non",
        "npp_nnonmyc",
        "mycorrhizal",
        "uptake"
    ],
    "NPP_NRETRANS": [
        "retranslocated",
        "npp_nretrans",
        "npp nretrans",
        "flux",
        "uptake"
    ],
    "NPP_NUPTAKE": [
        "used",
        "npp_nuptake",
        "total",
        "npp nuptake",
        "uptake",
        "fun"
    ],
    "NRETRANS_REG": [
        "retranslocated",
        "nretrans reg",
        "flux",
        "nretrans_reg",
        "uptake"
    ],
    "NRETRANS_SEASON": [
        "retranslocated",
        "nretrans season",
        "flux",
        "nretrans_season",
        "uptake"
    ],
    "NRETRANS_STRESS": [
        "retranslocated",
        "flux",
        "nretrans_stress",
        "nretrans stress",
        "uptake"
    ],
    "NRETRANS": [
        "flux",
        "retranslocated",
        "uptake",
        "nretrans"
    ],
    "NUPTAKE_NPP_FRACTION": [
        "used",
        "frac",
        "nuptake_npp_fraction",
        "npp",
        "uptake",
        "nuptake npp fraction"
    ],
    "NUPTAKE": [
        "nuptake",
        "total",
        "fun",
        "uptake"
    ],
    "O_SCALAR": [
        "o scalar",
        "o_scalar",
        "reduced",
        "due",
        "decomposition",
        "fraction",
        "which"
    ],
    "PARVEGLN": [
        "local",
        "absorbed",
        "par",
        "vegetation",
        "parvegln",
        "noon"
    ],
    "PBOT": [
        "columns",
        "downscaled",
        "atmospheric",
        "pressure",
        "pbot",
        "surface"
    ],
    "PCH4": [
        "atmospheric",
        "partial",
        "pch4",
        "pressure"
    ],
    "POT_F_DENIT": [
        "temp",
        "pot f denit",
        "pot_f_denit",
        "temperature",
        "potential",
        "denitrification",
        "flux",
        "thermal"
    ],
    "POT_F_NIT": [
        "pot f nit",
        "pot_f_nit",
        "temp",
        "nitrification",
        "temperature",
        "potential",
        "flux",
        "thermal"
    ],
    "Q2M": [
        "q2m",
        "specific",
        "humidity"
    ],
    "QBOT": [
        "columns",
        "downscaled",
        "specific",
        "atmospheric",
        "qbot",
        "humidity"
    ],
    "QCHARGE": [
        "vegetated",
        "landunits",
        "qcharge",
        "recharge",
        "rate",
        "aquifer"
    ],
    "QDRAI_XS": [
        "saturation",
        "qdrai xs",
        "excess",
        "qdrai_xs",
        "drainage"
    ],
    "QFLOOD": [
        "flooding",
        "qflood",
        "from",
        "river",
        "runoff"
    ],
    "QFLX_DEW_GRND": [
        "qflx_dew_grnd",
        "formation",
        "ground",
        "dew",
        "qflx dew grnd",
        "surface"
    ],
    "QFLX_DEW_SNOW": [
        "pack",
        "snow",
        "dew",
        "qflx_dew_snow",
        "qflx dew snow",
        "surface",
        "added"
    ],
    "QFLX_EVAP_TOT": [
        "qflx evap tot",
        "qflx_evap_tot"
    ],
    "QFLX_SNOW_DRAIN_ICE": [
        "melt",
        "precipitation",
        "rainfall",
        "pack",
        "qflx_snow_drain_ice",
        "qflx snow drain ice",
        "from",
        "snow",
        "drainage",
        "rain"
    ],
    "QFLX_SUB_SNOW_ICE": [
        "pack",
        "sublimation",
        "from",
        "snow",
        "qflx_sub_snow_ice",
        "qflx sub snow ice",
        "rate"
    ],
    "QH2OSFC": [
        "water",
        "surface",
        "runoff",
        "qh2osfc"
    ],
    "QICE_FRZ": [
        "qice_frz",
        "ice",
        "qice frz",
        "growth"
    ],
    "QICE_MELT": [
        "melt",
        "ice",
        "qice melt",
        "qice_melt"
    ],
    "QICE": [
        "growth",
        "ice",
        "melt",
        "qice"
    ],
    "QINFL": [
        "qinfl",
        "infiltration"
    ],
    "QIRRIG": [
        "through",
        "water",
        "qirrig",
        "irrigation",
        "added"
    ],
    "QRGWL": [
        "only",
        "runoff",
        "liquid",
        "surface",
        "qrgwl",
        "glaciers"
    ],
    "QRUNOFF_ICE": [
        "qrunoff ice",
        "incl",
        "not",
        "runoff",
        "total",
        "liquid",
        "qrunoff_ice"
    ],
    "QRUNOFF_ICE_TO_COUPLER": [
        "ice",
        "qrunoff_ice_to_coupler",
        "coupler",
        "runoff",
        "total",
        "sent",
        "qrunoff ice to coupler"
    ],
    "QRUNOFF_TO_COUPLER": [
        "coupler",
        "qrunoff_to_coupler",
        "qrunoff to coupler",
        "runoff",
        "total",
        "sent",
        "liquid"
    ],
    "QSNOCPLIQ": [
        "qsnocpliq",
        "excess",
        "snow",
        "liquid",
        "capping",
        "due"
    ],
    "QSNOFRZ_ICE": [
        "snow",
        "qsnofrz_ice",
        "integrated",
        "column",
        "qsnofrz ice",
        "rate",
        "freezing"
    ],
    "QSNOMELT_ICE": [
        "melt",
        "ice",
        "qsnomelt ice",
        "only",
        "landunits",
        "qsnomelt_ice",
        "temp",
        "snow",
        "temperature",
        "thermal"
    ],
    "QSNOMELT": [
        "melt",
        "qsnomelt",
        "snow",
        "rate"
    ],
    "QSNO_TEMPUNLOAD": [
        "qsno_tempunload",
        "qsno tempunload",
        "temp",
        "canopy",
        "snow",
        "unloading",
        "temperature",
        "thermal"
    ],
    "QSNO_WINDUNLOAD": [
        "canopy",
        "snow",
        "unloading",
        "wind",
        "qsno_windunload",
        "qsno windunload"
    ],
    "QSNWCPICE": [
        "qsnwcpice",
        "excess",
        "snow",
        "solid",
        "capping",
        "due"
    ],
    "QSOIL_ICE": [
        "ice",
        "only",
        "landunits",
        "ground",
        "qsoil_ice",
        "qsoil ice",
        "evaporation"
    ],
    "RAIN_FROM_ATM": [
        "precipitation",
        "rainfall",
        "atmospheric",
        "from",
        "atmosphere",
        "received",
        "rain_from_atm",
        "rain from atm",
        "rain"
    ],
    "RAIN_ICE": [
        "rain ice",
        "precipitation",
        "rainfall",
        "atmospheric",
        "after",
        "snow",
        "rain_ice",
        "rain"
    ],
    "RC13_CANAIR": [
        "canopy",
        "for",
        "rc13 canair",
        "air",
        "rc13_canair"
    ],
    "RC13_PSNSHA": [
        "photosynthesis",
        "for",
        "rc13_psnsha",
        "rc13 psnsha",
        "shaded"
    ],
    "RC13_PSNSUN": [
        "rc13 psnsun",
        "photosynthesis",
        "for",
        "sunlit",
        "rc13_psnsun"
    ],
    "RSSHA": [
        "stomatal",
        "rssha",
        "resistance",
        "shaded",
        "leaf"
    ],
    "RSSUN": [
        "stomatal",
        "rssun",
        "resistance",
        "sunlit",
        "leaf"
    ],
    "SABG_PEN": [
        "rural",
        "top",
        "sabg_pen",
        "rad",
        "solar",
        "penetrating",
        "sabg pen"
    ],
    "SLASH_HARVESTC": [
        "carbon",
        "slash harvestc",
        "slash",
        "litter",
        "slash_harvestc",
        "harvest"
    ],
    "SMIN_NH4": [
        "smin_nh4",
        "soil",
        "smin nh4",
        "mineral"
    ],
    "SMIN_NO3_LEACHED": [
        "soil",
        "pool",
        "loss",
        "leaching",
        "smin_no3_leached",
        "smin no3 leached"
    ],
    "SMIN_NO3_RUNOFF": [
        "smin_no3_runoff",
        "soil",
        "pool",
        "loss",
        "smin no3 runoff",
        "runoff"
    ],
    "SMIN_NO3": [
        "soil",
        "smin_no3",
        "mineral",
        "smin no3"
    ],
    "SMINN_TO_PLANT_FUN": [
        "sminn_to_plant_fun",
        "soil",
        "temp",
        "sminn to plant fun",
        "total",
        "temperature",
        "uptake",
        "fun",
        "thermal"
    ],
    "SMP": [
        "soil",
        "vegetated",
        "landunits",
        "potential",
        "matric",
        "smp"
    ],
    "SNOINTABS": [
        "snointabs",
        "absorbed",
        "solar",
        "lower",
        "fraction",
        "incoming"
    ],
    "SNOTXMASS_ICE": [
        "layer",
        "mass",
        "snow",
        "snotxmass ice",
        "temperature",
        "times",
        "snotxmass_ice"
    ],
    "SNOUNLOAD": [
        "unloading",
        "snow",
        "snounload",
        "canopy"
    ],
    "SNOW_DEPTH": [
        "snow depth",
        "snow",
        "covered",
        "snow_depth",
        "area",
        "height"
    ],
    "SNOW_FROM_ATM": [
        "atmospheric",
        "from",
        "snow",
        "atmosphere",
        "snow from atm",
        "received",
        "snow_from_atm"
    ],
    "SNOWICE_ICE": [
        "ice",
        "snowice ice",
        "only",
        "snowice_ice",
        "landunits",
        "snow"
    ],
    "SNOW_ICE": [
        "rain",
        "atmospheric",
        "after",
        "snow",
        "snow_ice",
        "snow ice"
    ],
    "SNOWLIQ_ICE": [
        "ice",
        "landunits",
        "water",
        "snow",
        "snowliq_ice",
        "liquid",
        "snowliq ice"
    ],
    "SNOW_PERSISTENCE": [
        "snow_persistence",
        "length",
        "snow",
        "cover",
        "snow persistence",
        "time",
        "continuous"
    ],
    "SNOW_SOURCES": [
        "snow_sources",
        "snow sources",
        "water",
        "snow",
        "sources",
        "liquid"
    ],
    "SOILC_CHANGE": [
        "soilc_change",
        "change",
        "soilc change",
        "soil"
    ],
    "SOILC_HR": [
        "heterotrophic",
        "soil",
        "soilc_hr",
        "respiration",
        "soilc hr"
    ],
    "SOILRESIS": [
        "resistance",
        "soil",
        "evaporation",
        "soilresis"
    ],
    "SOMC_FIRE": [
        "peat",
        "loss",
        "burning",
        "somc fire",
        "somc_fire",
        "due"
    ],
    "SOM_C_LEACHED": [
        "pools",
        "from",
        "som c leached",
        "total",
        "som",
        "flux",
        "som_c_leached"
    ],
    "SWBGT_R": [
        "rural",
        "globe",
        "temp",
        "wetbulb",
        "temperature",
        "swbgt_r",
        "simplified",
        "swbgt r",
        "thermal"
    ],
    "SWBGT": [
        "globe",
        "temp",
        "swbgt",
        "wetbulb",
        "simplified"
    ],
    "SWBGT_U": [
        "globe",
        "temp",
        "swbgt u",
        "wetbulb",
        "temperature",
        "urban",
        "swbgt_u",
        "simplified",
        "thermal"
    ],
    "TBOT": [
        "columns",
        "downscaled",
        "atmospheric",
        "air",
        "temperature",
        "tbot"
    ],
    "TG_ICE": [
        "ice",
        "tg ice",
        "landunits",
        "only",
        "ground",
        "tg_ice",
        "temperature"
    ],
    "TH2OSFC": [
        "water",
        "th2osfc",
        "surface",
        "temperature"
    ],
    "TKE1": [
        "top",
        "lake",
        "level",
        "thermal",
        "eddy",
        "tke1"
    ],
    "TLAKE": [
        "lake",
        "temperature",
        "tlake"
    ],
    "TOPO_COL_ICE": [
        "ice",
        "topo col ice",
        "column",
        "topographic",
        "level",
        "topo_col_ice",
        "height"
    ],
    "TOTCOLCH4": [
        "non",
        "for",
        "total",
        "lake",
        "totcolch4",
        "belowground"
    ],
    "TOTECOSYSN": [
        "pools",
        "total",
        "excluding",
        "totecosysn",
        "ecosystem",
        "product"
    ],
    "TOTLITC_1m": [
        "carbon",
        "totlitc 1m",
        "total",
        "meter",
        "depth",
        "litter",
        "totlitc_1m"
    ],
    "TOTLITN_1m": [
        "totlitn 1m",
        "meter",
        "total",
        "litter",
        "totlitn_1m"
    ],
    "TOTSOMN_1m": [
        "soil",
        "organic",
        "total",
        "meter",
        "matter",
        "totsomn_1m",
        "totsomn 1m"
    ],
    "TOTVEGN": [
        "total",
        "totvegn",
        "nitrogen",
        "vegetation"
    ],
    "TOT_WOODPRODC_LOSS": [
        "loss",
        "temp",
        "from",
        "total",
        "product",
        "temperature",
        "tot woodprodc loss",
        "tot_woodprodc_loss",
        "wood",
        "thermal"
    ],
    "TOT_WOODPRODN_LOSS": [
        "loss",
        "temp",
        "tot woodprodn loss",
        "from",
        "tot_woodprodn_loss",
        "total",
        "temperature",
        "product",
        "wood",
        "thermal"
    ],
    "TOT_WOODPRODN": [
        "tot_woodprodn",
        "temp",
        "total",
        "tot woodprodn",
        "temperature",
        "product",
        "wood",
        "thermal"
    ],
    "TPU25T": [
        "tpu25t",
        "profile",
        "tpu",
        "canopy"
    ],
    "TSA_ICE": [
        "ice",
        "only",
        "landunits",
        "tsa ice",
        "air",
        "tsa_ice",
        "temperature"
    ],
    "T_SCALAR": [
        "temp",
        "t_scalar",
        "inhibition",
        "decomposition",
        "temperature",
        "t scalar",
        "thermal"
    ],
    "TSL": [
        "layer",
        "soil",
        "temperature",
        "near",
        "surface",
        "tsl"
    ],
    "TSOI_10CM": [
        "top",
        "soil",
        "tsoi_10cm",
        "temperature",
        "tsoi 10cm"
    ],
    "U10_DUST": [
        "dust",
        "for",
        "model",
        "u10_dust",
        "wind",
        "u10 dust"
    ],
    "VCMX25T": [
        "profile",
        "vcmx25t",
        "canopy"
    ],
    "Vcmx25Z": [
        "canopy",
        "predicted",
        "model",
        "profile",
        "luna",
        "vcmx25z"
    ],
    "VEGWP": [
        "water",
        "vegwp",
        "vegetation",
        "for",
        "potential",
        "matric"
    ],
    "VOLRMCH": [
        "volrmch",
        "channel",
        "water",
        "main",
        "river"
    ],
    "VOLR": [
        "volr",
        "storage",
        "water",
        "channel",
        "river",
        "total"
    ],
    "WA": [
        "vegetated",
        "water",
        "the",
        "aquifer",
        "unconfined"
    ],
    "WBT_R": [
        "rural",
        "temp",
        "wbt r",
        "wet",
        "stull",
        "bulb",
        "temperature",
        "wbt_r",
        "thermal"
    ],
    "WBT": [
        "bulb",
        "wbt",
        "stull",
        "wet"
    ],
    "WBT_U": [
        "wbt u",
        "temp",
        "wet",
        "wbt_u",
        "stull",
        "urban",
        "bulb",
        "temperature",
        "thermal"
    ],
    "WIND": [
        "atmospheric",
        "velocity",
        "magnitude",
        "wind"
    ],
    "W_SCALAR": [
        "moisture",
        "w_scalar",
        "dryness",
        "inhibition",
        "decomposition",
        "w scalar"
    ],
    "WTGQ": [
        "tracer",
        "surface",
        "wtgq",
        "conductance"
    ],
    "ZWT_CH4_UNSAT": [
        "methane",
        "table",
        "zwt ch4 unsat",
        "temp",
        "water",
        "for",
        "depth",
        "zwt_ch4_unsat",
        "temperature",
        "thermal"
    ],
    "ZWT_PERCH": [
        "zwt perch",
        "table",
        "vegetated",
        "temp",
        "water",
        "zwt_perch",
        "depth",
        "perched",
        "temperature",
        "thermal"
    ],
    "ZWT": [
        "vegetated",
        "table",
        "landunits",
        "water",
        "depth",
        "zwt"
    ],
    "diazC_zint_100m": [
        "diazotroph",
        "diazc_zint_100m",
        "carbon",
        "integral",
        "vertical",
        "temp",
        "temperature",
        "diazc zint 100m",
        "thermal"
    ],
    "DpCO2_2": [
        "dpco2_2",
        "dpco2 2"
    ],
    "ECOSYS_XKW_2": [
        "ecosys",
        "fluxes",
        "xkw",
        "for",
        "ecosys xkw 2",
        "ecosys_xkw_2"
    ],
    "FG_CO2_2": [
        "fg co2 2",
        "dic",
        "gas",
        "flux",
        "surface",
        "fg_co2_2"
    ],
    "spCaCO3_zint_100m": [
        "spcaco3_zint_100m",
        "temp",
        "integral",
        "vertical",
        "small",
        "phyto",
        "temperature",
        "spcaco3 zint 100m",
        "thermal"
    ],
    "SST2": [
        "surface",
        "potential",
        "temperature",
        "sst2"
    ],
    "STF_O2_2": [
        "oxygen",
        "dissolved",
        "stf o2 2",
        "flux",
        "surface",
        "stf_o2_2"
    ],
    "XBLT_2": [
        "layer",
        "temp",
        "boundary",
        "maximum",
        "depth",
        "xblt 2",
        "temperature",
        "xblt_2",
        "thermal"
    ],
    "XMXL_2": [
        "layer",
        "maximum",
        "xmxl_2",
        "depth",
        "mixed",
        "xmxl 2"
    ],
    "CFC_ATM_PRESS": [
        "cfc_atm_press",
        "cfc",
        "fluxes",
        "atmospheric",
        "for",
        "pressure",
        "cfc atm press"
    ],
    "CFC_IFRAC": [
        "ice",
        "cfc",
        "fluxes",
        "cfc ifrac",
        "for",
        "cfc_ifrac",
        "fraction"
    ],
    "CFC_XKW": [
        "cfc",
        "fluxes",
        "xkw",
        "for",
        "cfc_xkw",
        "cfc xkw"
    ],
    "DCO2STAR_ALT_CO2": [
        "temp",
        "alternative",
        "dco2star alt co2",
        "star",
        "temperature",
        "dco2star_alt_co2",
        "thermal"
    ],
    "DCO2STAR": [
        "dco2star",
        "star"
    ],
    "DIA_DEPTH": [
        "dia depth",
        "diabatic",
        "depth",
        "the",
        "dia_depth",
        "region"
    ],
    "DON_prod": [
        "don prod",
        "don",
        "production",
        "don_prod"
    ],
    "DOP_prod": [
        "dop prod",
        "dop",
        "production",
        "dop_prod"
    ],
    "dTEMP_NEG_2D": [
        "temp",
        "timestep",
        "dtemp_neg_2d",
        "min",
        "temperature",
        "neg",
        "dtemp neg 2d",
        "column",
        "thermal"
    ],
    "dTEMP_POS_2D": [
        "dtemp_pos_2d",
        "temp",
        "dtemp pos 2d",
        "column",
        "pos",
        "temperature",
        "timestep",
        "max",
        "thermal"
    ],
    "ECOSYS_ATM_PRESS": [
        "ecosys",
        "fluxes",
        "atmospheric",
        "ecosys atm press",
        "for",
        "pressure",
        "ecosys_atm_press"
    ],
    "ECOSYS_XKW": [
        "ecosys",
        "ecosys xkw",
        "fluxes",
        "ecosys_xkw",
        "xkw",
        "for"
    ],
    "Fe_scavenge_rate": [
        "fe_scavenge_rate",
        "scavenging",
        "fe scavenge rate",
        "rate",
        "iron"
    ],
    "Fe_scavenge": [
        "fe scavenge",
        "iron",
        "fe_scavenge",
        "scavenging"
    ],
    "FvICE_ALK": [
        "ice",
        "alkalinity",
        "fvice alk",
        "fvice_alk",
        "flux",
        "surface",
        "virtual"
    ],
    "FvICE_DIC": [
        "carbon",
        "fvice_dic",
        "inorganic",
        "fvice dic",
        "dissolved",
        "surface",
        "virtual"
    ],
    "FvPER_ALK": [
        "alkalinity",
        "per",
        "fvper alk",
        "fvper_alk",
        "flux",
        "surface",
        "virtual"
    ],
    "FvPER_DIC": [
        "carbon",
        "inorganic",
        "dissolved",
        "surface",
        "fvper_dic",
        "fvper dic",
        "virtual"
    ],
    "FW": [
        "flux",
        "freshwater"
    ],
    "H2CO3": [
        "h2co3",
        "carbonic",
        "acid",
        "concentration"
    ],
    "HBLT": [
        "boundary",
        "hblt",
        "depth",
        "layer"
    ],
    "HDIFS": [
        "tendency",
        "vertically",
        "hdifs",
        "integrated",
        "horz",
        "diff"
    ],
    "HLS_SUBM": [
        "horizontal",
        "used",
        "hls_subm",
        "length",
        "submeso",
        "scale",
        "hls subm"
    ],
    "INT_DEPTH": [
        "temp",
        "depth",
        "interior",
        "int depth",
        "the",
        "temperature",
        "thermal",
        "which",
        "region",
        "int_depth"
    ],
    "IRON_FLUX": [
        "iron flux",
        "atmospheric",
        "iron_flux",
        "flux",
        "iron"
    ],
    "Jint_100m_ALK": [
        "alkalinity",
        "temp",
        "jint 100m alk",
        "vertical",
        "source",
        "term",
        "jint_100m_alk",
        "temperature",
        "sink",
        "thermal"
    ],
    "Jint_100m_DIC": [
        "temp",
        "carbon",
        "inorganic",
        "source",
        "temperature",
        "sink",
        "jint 100m dic",
        "dissolved",
        "jint_100m_dic",
        "thermal"
    ],
    "Jint_100m_DOC": [
        "jint_100m_doc",
        "organic",
        "carbon",
        "temp",
        "source",
        "jint 100m doc",
        "temperature",
        "sink",
        "dissolved",
        "thermal"
    ],
    "Jint_100m_Fe": [
        "temp",
        "inorganic",
        "jint 100m fe",
        "source",
        "temperature",
        "jint_100m_fe",
        "sink",
        "dissolved",
        "iron",
        "thermal"
    ],
    "Jint_100m_NH4": [
        "jint 100m nh4",
        "temp",
        "source",
        "jint_100m_nh4",
        "term",
        "ammonia",
        "temperature",
        "sink",
        "dissolved",
        "thermal"
    ],
    "Jint_100m_NO3": [
        "jint 100m no3",
        "temp",
        "inorganic",
        "nitrate",
        "source",
        "temperature",
        "sink",
        "dissolved",
        "jint_100m_no3",
        "thermal"
    ],
    "Jint_100m_O2": [
        "oxygen",
        "temp",
        "source",
        "jint_100m_o2",
        "term",
        "jint 100m o2",
        "temperature",
        "sink",
        "dissolved",
        "thermal"
    ],
    "Jint_100m_PO4": [
        "temp",
        "inorganic",
        "source",
        "temperature",
        "sink",
        "jint 100m po4",
        "dissolved",
        "phosphate",
        "jint_100m_po4",
        "thermal"
    ],
    "Jint_100m_SiO3": [
        "temp",
        "jint_100m_sio3",
        "inorganic",
        "source",
        "jint 100m sio3",
        "silicate",
        "temperature",
        "sink",
        "dissolved",
        "thermal"
    ],
    "KVMIX_M": [
        "vertical",
        "mixing",
        "kvmix_m",
        "viscosity",
        "kvmix m",
        "due",
        "tidal"
    ],
    "MELT_F": [
        "melt",
        "melt_f",
        "coupler",
        "temp",
        "melt f",
        "from",
        "temperature",
        "flux",
        "thermal"
    ],
    "MELTH_F": [
        "melt",
        "heat",
        "coupler",
        "from",
        "melth_f",
        "melth f",
        "flux"
    ],
    "NHy_FLUX": [
        "nhy flux",
        "nhy_flux",
        "from",
        "atmosphere",
        "nhy",
        "flux"
    ],
    "N_SALT": [
        "northward",
        "n salt",
        "salt",
        "n_salt",
        "transport"
    ],
    "O2_CONSUMPTION": [
        "o2 consumption",
        "consumption",
        "o2_consumption"
    ],
    "O2_PRODUCTION": [
        "o2 production",
        "o2_production",
        "production"
    ],
    "O2SAT": [
        "o2sat",
        "saturation"
    ],
    "PH_ALT_CO2": [
        "temp",
        "alternative",
        "ph alt co2",
        "temperature",
        "surface",
        "ph_alt_co2",
        "thermal"
    ],
    "P_iron_FLUX_IN": [
        "cell",
        "p iron flux in",
        "p_iron_flux_in",
        "flux",
        "into"
    ],
    "P_iron_PROD": [
        "production",
        "p iron prod",
        "p_iron_prod"
    ],
    "QSW_HBL": [
        "heat",
        "short",
        "wave",
        "qsw_hbl",
        "solar",
        "qsw hbl",
        "flux"
    ],
    "QSW_HTP": [
        "heat",
        "qsw htp",
        "short",
        "wave",
        "solar",
        "flux",
        "qsw_htp"
    ],
    "RESID_S": [
        "resid_s",
        "resid s",
        "free",
        "flux",
        "surface",
        "residual"
    ],
    "SALT_F": [
        "coupler",
        "temp",
        "from",
        "salt f",
        "salt",
        "temperature",
        "salt_f",
        "flux",
        "thermal"
    ],
    "SCHMIDT_CO2": [
        "schmidt co2",
        "temp",
        "schmidt",
        "number",
        "temperature",
        "schmidt_co2",
        "thermal"
    ],
    "SCHMIDT_O2": [
        "temp",
        "schmidt",
        "number",
        "temperature",
        "schmidt_o2",
        "schmidt o2",
        "thermal"
    ],
    "SENH_F": [
        "heat",
        "coupler",
        "senh f",
        "from",
        "senh_f",
        "sensible",
        "flux"
    ],
    "SFWF_WRST": [
        "salt",
        "weak",
        "due",
        "sfwf_wrst",
        "sfwf wrst",
        "flux",
        "virtual"
    ],
    "SiO2_FLUX_IN": [
        "cell",
        "sio2 flux in",
        "sio2_flux_in",
        "flux",
        "into"
    ],
    "SNOW_F": [
        "coupler",
        "snow f",
        "from",
        "snow",
        "snow_f",
        "flux"
    ],
    "SSH2": [
        "ssh",
        "ssh2"
    ],
    "STF_CFC11": [
        "stf cfc11",
        "excludes",
        "term",
        "fvice",
        "flux",
        "surface",
        "stf_cfc11"
    ],
    "STF_CFC12": [
        "excludes",
        "term",
        "fvice",
        "flux",
        "surface",
        "stf cfc12",
        "stf_cfc12"
    ],
    "STF_O2": [
        "oxygen",
        "stf o2",
        "excludes",
        "stf_o2",
        "dissolved",
        "flux",
        "surface"
    ],
    "TBLT": [
        "layer",
        "minimum",
        "boundary",
        "depth",
        "tblt"
    ],
    "tend_zint_100m_ALK": [
        "alkalinity",
        "tendency",
        "temp",
        "integral",
        "vertical",
        "temperature",
        "tend_zint_100m_alk",
        "tend zint 100m alk",
        "thermal"
    ],
    "tend_zint_100m_DIC_ALT_CO2": [
        "tendency",
        "temp",
        "carbon",
        "inorganic",
        "dissolved",
        "alternative",
        "tend_zint_100m_dic_alt_co2",
        "temperature",
        "tend zint 100m dic alt co2",
        "thermal"
    ],
    "tend_zint_100m_DIC": [
        "tend_zint_100m_dic",
        "tend zint 100m dic",
        "tendency",
        "carbon",
        "temp",
        "vertical",
        "inorganic",
        "temperature",
        "dissolved",
        "thermal"
    ],
    "tend_zint_100m_DOC": [
        "tend zint 100m doc",
        "organic",
        "tendency",
        "carbon",
        "temp",
        "vertical",
        "tend_zint_100m_doc",
        "temperature",
        "dissolved",
        "thermal"
    ],
    "tend_zint_100m_Fe": [
        "tend zint 100m fe",
        "tendency",
        "temp",
        "vertical",
        "inorganic",
        "tend_zint_100m_fe",
        "temperature",
        "dissolved",
        "iron",
        "thermal"
    ],
    "tend_zint_100m_NH4": [
        "tendency",
        "temp",
        "integral",
        "vertical",
        "ammonia",
        "tend_zint_100m_nh4",
        "temperature",
        "dissolved",
        "tend zint 100m nh4",
        "thermal"
    ],
    "tend_zint_100m_NO3": [
        "tendency",
        "temp",
        "vertical",
        "nitrate",
        "inorganic",
        "temperature",
        "tend_zint_100m_no3",
        "dissolved",
        "thermal",
        "tend zint 100m no3"
    ],
    "tend_zint_100m_O2": [
        "oxygen",
        "tendency",
        "temp",
        "integral",
        "vertical",
        "tend zint 100m o2",
        "temperature",
        "thermal",
        "dissolved",
        "tend_zint_100m_o2"
    ],
    "tend_zint_100m_PO4": [
        "tendency",
        "temp",
        "tend zint 100m po4",
        "vertical",
        "inorganic",
        "dissolved",
        "temperature",
        "tend_zint_100m_po4",
        "phosphate",
        "thermal"
    ],
    "TFW_S": [
        "salt",
        "due",
        "tfw_s",
        "tfw s",
        "flux",
        "freshwater"
    ],
    "TFW_T": [
        "tfw t",
        "due",
        "tfw_t",
        "flux",
        "freshwater"
    ],
    "TLT": [
        "layer",
        "tlt",
        "thickness",
        "transition"
    ],
    "TMXL": [
        "layer",
        "minimum",
        "depth",
        "mixed",
        "tmxl"
    ],
    "TPOWER": [
        "used",
        "tpower",
        "vertical",
        "energy",
        "mixing"
    ],
    "VDC_S": [
        "diffusivity",
        "vertical",
        "vdc_s",
        "diabatic",
        "vdc s",
        "total",
        "salt"
    ],
    "VNS_ISOP": [
        "tendency",
        "vns_isop",
        "salt",
        "vns isop",
        "grid",
        "flux",
        "dir"
    ],
    "VNS_SUBM": [
        "dir",
        "tendency",
        "salt",
        "vns subm",
        "grid",
        "flux",
        "vns_subm"
    ],
    "VNT_SUBM": [
        "heat",
        "tendency",
        "temp",
        "vnt_subm",
        "grid",
        "temperature",
        "vnt subm",
        "flux",
        "thermal",
        "dir"
    ],
    "VVC": [
        "vvc",
        "vertical",
        "total",
        "viscosity",
        "momentum"
    ],
    "WVEL2": [
        "vertical",
        "wvel2",
        "velocity"
    ],
    "XBLT": [
        "layer",
        "boundary",
        "maximum",
        "xblt",
        "depth"
    ],
    "zsatarag": [
        "depth",
        "aragonite",
        "zsatarag",
        "saturation"
    ],
    "zsatcalc": [
        "zsatcalc",
        "depth",
        "calcite",
        "saturation"
    ],
    "DIA_IMPVF_DOC": [
        "dia impvf doc",
        "face",
        "across",
        "dia_impvf_doc",
        "flux",
        "doc",
        "bottom"
    ],
    "DIA_IMPVF_Fe": [
        "from",
        "dia_impvf_fe",
        "face",
        "across",
        "dia impvf fe",
        "flux",
        "bottom"
    ],
    "DIA_IMPVF_O2": [
        "from",
        "dia_impvf_o2",
        "dia impvf o2",
        "face",
        "across",
        "flux",
        "bottom"
    ],
    "HDIFB_DOC": [
        "horizontal",
        "diffusive",
        "hdifb_doc",
        "hdifb doc",
        "across",
        "flux",
        "doc"
    ],
    "HDIFB_Fe": [
        "horizontal",
        "hdifb fe",
        "diffusive",
        "hdifb_fe",
        "across",
        "flux",
        "bottom"
    ],
    "HDIFB_O2": [
        "horizontal",
        "diffusive",
        "hdifb o2",
        "across",
        "flux",
        "hdifb_o2",
        "bottom"
    ],
    "HDIFE_DOC": [
        "horizontal",
        "diffusive",
        "hdife_doc",
        "hdife doc",
        "grid",
        "flux",
        "doc"
    ],
    "HDIFE_Fe": [
        "horizontal",
        "diffusive",
        "direction",
        "grid",
        "hdife fe",
        "flux",
        "hdife_fe"
    ],
    "HDIFE_O2": [
        "horizontal",
        "diffusive",
        "direction",
        "hdife o2",
        "hdife_o2",
        "grid",
        "flux"
    ],
    "HDIFN_DOC": [
        "horizontal",
        "diffusive",
        "hdifn doc",
        "grid",
        "flux",
        "hdifn_doc",
        "doc"
    ],
    "HDIFN_Fe": [
        "horizontal",
        "hdifn_fe",
        "diffusive",
        "direction",
        "grid",
        "flux",
        "hdifn fe"
    ],
    "HDIFN_O2": [
        "horizontal",
        "diffusive",
        "direction",
        "grid",
        "flux",
        "hdifn o2",
        "hdifn_o2"
    ],
    "J_ALK": [
        "j alk",
        "alkalinity",
        "source",
        "term",
        "sink",
        "j_alk"
    ],
    "J_Fe": [
        "inorganic",
        "source",
        "sink",
        "dissolved",
        "j_fe",
        "j fe",
        "iron"
    ],
    "J_NH4": [
        "j nh4",
        "source",
        "term",
        "ammonia",
        "sink",
        "dissolved",
        "j_nh4"
    ],
    "J_PO4": [
        "j_po4",
        "inorganic",
        "source",
        "j po4",
        "sink",
        "dissolved",
        "phosphate"
    ],
    "KPP_SRC_Fe": [
        "kpp",
        "tendency",
        "kpp_src_fe",
        "kpp src fe",
        "non",
        "local",
        "from"
    ],
    "KPP_SRC_O2": [
        "kpp",
        "tendency",
        "local",
        "non",
        "from",
        "kpp src o2",
        "kpp_src_o2"
    ],
    "UE_DOC": [
        "ue_doc",
        "direction",
        "ue doc",
        "grid",
        "flux",
        "doc"
    ],
    "UE_Fe": [
        "direction",
        "grid",
        "ue_fe",
        "flux",
        "ue fe"
    ],
    "UE_O2": [
        "direction",
        "ue o2",
        "ue_o2",
        "grid",
        "flux"
    ],
    "VN_DOC": [
        "vn doc",
        "vn_doc",
        "direction",
        "flux",
        "grid",
        "doc"
    ],
    "VN_Fe": [
        "direction",
        "vn_fe",
        "grid",
        "vn fe",
        "flux"
    ],
    "VN_O2": [
        "vn o2",
        "direction",
        "grid",
        "vn_o2",
        "flux"
    ],
    "WT_DOC": [
        "top",
        "temp",
        "wt doc",
        "face",
        "across",
        "temperature",
        "flux",
        "doc",
        "wt_doc",
        "thermal"
    ],
    "WT_Fe": [
        "top",
        "temp",
        "wt_fe",
        "face",
        "across",
        "temperature",
        "wt fe",
        "flux",
        "thermal"
    ],
    "WT_O2": [
        "top",
        "temp",
        "wt o2",
        "face",
        "across",
        "temperature",
        "wt_o2",
        "flux",
        "thermal"
    ],
    "CaCO3_form_zint_2": [
        "temp",
        "formation",
        "integral",
        "vertical",
        "caco3_form_zint_2",
        "total",
        "caco3 form zint 2",
        "temperature",
        "thermal"
    ],
    "diatChl_SURF": [
        "chlorophyll",
        "diatchl_surf",
        "diatchl surf",
        "diatom",
        "surface",
        "value"
    ],
    "diatC_zint_100m": [
        "diatc_zint_100m",
        "diatc zint 100m",
        "temp",
        "carbon",
        "integral",
        "vertical",
        "temperature",
        "diatom",
        "thermal"
    ],
    "diazChl_SURF": [
        "chlorophyll",
        "diazotroph",
        "diazchl surf",
        "diazchl_surf",
        "surface",
        "value"
    ],
    "ECOSYS_IFRAC_2": [
        "ecosys_ifrac_2",
        "ice",
        "ecosys",
        "ecosys ifrac 2",
        "fluxes",
        "for",
        "fraction"
    ],
    "HBLT_2": [
        "layer",
        "temp",
        "boundary",
        "depth",
        "hblt 2",
        "temperature",
        "thermal",
        "hblt_2"
    ],
    "HMXL_2": [
        "layer",
        "depth",
        "mixed",
        "hmxl_2",
        "hmxl 2"
    ],
    "HMXL_DR_2": [
        "layer",
        "hmxl_dr_2",
        "depth",
        "mixed",
        "hmxl dr 2",
        "density"
    ],
    "photoC_diat_zint_2": [
        "photoc_diat_zint_2",
        "temp",
        "integral",
        "vertical",
        "fixation",
        "temperature",
        "photoc diat zint 2",
        "diatom",
        "thermal"
    ],
    "photoC_diaz_zint_2": [
        "diazotroph",
        "temp",
        "integral",
        "vertical",
        "fixation",
        "photoc diaz zint 2",
        "temperature",
        "photoc_diaz_zint_2",
        "thermal"
    ],
    "photoC_sp_zint_2": [
        "photoc sp zint 2",
        "temp",
        "integral",
        "photoc_sp_zint_2",
        "vertical",
        "small",
        "fixation",
        "phyto",
        "temperature",
        "thermal"
    ],
    "spChl_SURF": [
        "chlorophyll",
        "spchl surf",
        "small",
        "phyto",
        "spchl_surf",
        "surface",
        "value"
    ],
    "spC_zint_100m": [
        "spc zint 100m",
        "temp",
        "carbon",
        "integral",
        "vertical",
        "small",
        "spc_zint_100m",
        "phyto",
        "temperature",
        "thermal"
    ],
    "SSH2_2": [
        "ssh2 2",
        "ssh",
        "ssh2_2"
    ],
    "SSH_2": [
        "ssh_2",
        "sea",
        "surface",
        "ssh 2",
        "height"
    ],
    "SSS": [
        "surface",
        "sss",
        "salinity",
        "sea"
    ],
    "TAUX_2": [
        "direction",
        "taux 2",
        "windstress",
        "taux_2",
        "grid"
    ],
    "TAUY_2": [
        "tauy 2",
        "direction",
        "windstress",
        "tauy_2",
        "grid"
    ],
    "WVEL_50m": [
        "velocity",
        "vertical",
        "depth",
        "wvel_50m",
        "wvel 50m"
    ],
    "zooC_zint_100m": [
        "temp",
        "carbon",
        "integral",
        "zooc_zint_100m",
        "vertical",
        "zooc zint 100m",
        "zooplankton",
        "temperature",
        "thermal"
    ],
    "co3_sat_arag": [
        "co3 sat arag",
        "concentration",
        "temp",
        "saturation",
        "aragonite",
        "co3_sat_arag",
        "temperature",
        "thermal"
    ],
    "co3": [
        "concentration",
        "co3"
    ],
    "diacZ": [
        "diacz",
        "unknown"
    ],
    "diat_agg": [
        "temp",
        "diat agg",
        "aggregation",
        "diat_agg",
        "temperature",
        "diatom",
        "thermal"
    ],
    "diatChl": [
        "chlorophyll",
        "diatom",
        "diatchl"
    ],
    "diatC": [
        "diatc",
        "diatom",
        "carbon"
    ],
    "diat_Fe_lim_Cweight_avg_100m": [
        "biomass",
        "diat fe lim cweight avg 100m",
        "carbon",
        "temp",
        "limitation",
        "temperature",
        "thermal",
        "diatom",
        "diat_fe_lim_cweight_avg_100m",
        "weighted"
    ],
    "diat_light_lim_Cweight_avg_100m": [
        "biomass",
        "temp",
        "carbon",
        "diat_light_lim_cweight_avg_100m",
        "diat light lim cweight avg 100m",
        "limitation",
        "light",
        "temperature",
        "diatom",
        "thermal"
    ],
    "diat_loss": [
        "diat loss",
        "temp",
        "temperature",
        "diat_loss",
        "thermal",
        "unknown"
    ],
    "diat_N_lim_Cweight_avg_100m": [
        "biomass",
        "diat_n_lim_cweight_avg_100m",
        "carbon",
        "temp",
        "limitation",
        "temperature",
        "thermal",
        "diatom",
        "weighted",
        "diat n lim cweight avg 100m"
    ],
    "diat_P_lim_Cweight_avg_100m": [
        "biomass",
        "temp",
        "carbon",
        "diat p lim cweight avg 100m",
        "limitation",
        "temperature",
        "thermal",
        "diat_p_lim_cweight_avg_100m",
        "diatom",
        "weighted"
    ],
    "diat_SiO3_lim_Cweight_avg_100m": [
        "biomass",
        "temp",
        "carbon",
        "diat_sio3_lim_cweight_avg_100m",
        "limitation",
        "weighted",
        "temperature",
        "thermal",
        "diatom",
        "diat sio3 lim cweight avg 100m"
    ],
    "diaz_agg": [
        "aggregation",
        "diazotroph",
        "diaz_agg",
        "diaz agg"
    ],
    "diazChl": [
        "chlorophyll",
        "diazotroph",
        "diazchl"
    ],
    "diaz_Fe_lim_Cweight_avg_100m": [
        "diazotroph",
        "biomass",
        "temp",
        "carbon",
        "limitation",
        "weighted",
        "temperature",
        "thermal",
        "diaz_fe_lim_cweight_avg_100m",
        "diaz fe lim cweight avg 100m"
    ],
    "diaz_light_lim_Cweight_avg_100m": [
        "diazotroph",
        "biomass",
        "temp",
        "carbon",
        "diaz light lim cweight avg 100m",
        "limitation",
        "diaz_light_lim_cweight_avg_100m",
        "light",
        "temperature",
        "thermal"
    ],
    "diaz_loss": [
        "diaz_loss",
        "diaz loss",
        "unknown"
    ],
    "diaz_P_lim_Cweight_avg_100m": [
        "diazotroph",
        "biomass",
        "temp",
        "carbon",
        "limitation",
        "diaz p lim cweight avg 100m",
        "temperature",
        "diaz_p_lim_cweight_avg_100m",
        "thermal",
        "weighted"
    ],
    "DpCO2_ALT_CO2": [
        "dpco2_alt_co2",
        "temp",
        "alternative",
        "temperature",
        "dpco2 alt co2",
        "thermal"
    ],
    "DpCO2": [
        "dpco2"
    ],
    "FG_ALT_CO2": [
        "surface",
        "temp",
        "alternative",
        "dic",
        "gas",
        "temperature",
        "flux",
        "fg_alt_co2",
        "fg alt co2",
        "thermal"
    ],
    "FG_CO2": [
        "fg co2",
        "dic",
        "fg_co2",
        "gas",
        "flux",
        "surface"
    ],
    "graze_diat": [
        "graze diat",
        "graze_diat",
        "unknown"
    ],
    "graze_diaz": [
        "graze diaz",
        "graze_diaz",
        "unknown"
    ],
    "graze_sp": [
        "graze sp",
        "graze_sp",
        "unknown"
    ],
    "O2": [
        "dissolved",
        "oxygen"
    ],
    "PAR_avg": [
        "cell",
        "par avg",
        "average",
        "par",
        "model",
        "par_avg",
        "over"
    ],
    "pCO2SURF": [
        "pco2surf",
        "surface"
    ],
    "PD": [
        "ref",
        "surface",
        "density",
        "potential"
    ],
    "pH_3D": [
        "ph 3d",
        "ph_3d"
    ],
    "PhotoC_diat": [
        "photoc diat",
        "photoc_diat",
        "unknown"
    ],
    "PhotoC_diaz": [
        "photoc diaz",
        "photoc_diaz",
        "unknown"
    ],
    "PhotoC_sp": [
        "photoc sp",
        "photoc_sp",
        "unknown"
    ],
    "PO4": [
        "dissolved",
        "phosphate",
        "inorganic",
        "po4"
    ],
    "POC_FLUX_100": [
        "poc_flux_100",
        "poc flux 100",
        "unknown"
    ],
    "SALT": [
        "salinity",
        "salt"
    ],
    "sp_agg": [
        "sp_agg",
        "small",
        "sp agg",
        "aggregation",
        "phyto"
    ],
    "spChl": [
        "spchl",
        "chlorophyll",
        "small",
        "phyto"
    ],
    "spC": [
        "spc",
        "small",
        "phyto",
        "carbon"
    ],
    "sp_Fe_lim_Cweight_avg_100m": [
        "sp fe lim cweight avg 100m",
        "biomass",
        "temp",
        "carbon",
        "small",
        "limitation",
        "phyto",
        "temperature",
        "sp_fe_lim_cweight_avg_100m",
        "thermal"
    ],
    "sp_light_lim_Cweight_avg_100m": [
        "temp",
        "sp light lim cweight avg 100m",
        "carbon",
        "sp_light_lim_cweight_avg_100m",
        "small",
        "limitation",
        "light",
        "phyto",
        "temperature",
        "thermal"
    ],
    "sp_loss": [
        "sp_loss",
        "sp loss",
        "unknown"
    ],
    "sp_N_lim_Cweight_avg_100m": [
        "biomass",
        "temp",
        "carbon",
        "sp_n_lim_cweight_avg_100m",
        "sp n lim cweight avg 100m",
        "small",
        "limitation",
        "phyto",
        "temperature",
        "thermal"
    ],
    "sp_P_lim_Cweight_avg_100m": [
        "sp p lim cweight avg 100m",
        "biomass",
        "temp",
        "carbon",
        "sp_p_lim_cweight_avg_100m",
        "small",
        "limitation",
        "phyto",
        "temperature",
        "thermal"
    ],
    "TEMP": [
        "thermal",
        "temperature",
        "temp",
        "potential"
    ],
    "UISOP": [
        "uisop",
        "velocity",
        "diagnostic",
        "direction",
        "grid",
        "bolus"
    ],
    "USUBM": [
        "velocity",
        "diagnostic",
        "direction",
        "submeso",
        "usubm",
        "grid"
    ],
    "UVEL": [
        "direction",
        "uvel",
        "velocity",
        "grid"
    ],
    "VISOP": [
        "velocity",
        "visop",
        "direction",
        "diagnostic",
        "grid",
        "bolus"
    ],
    "VSUBM": [
        "velocity",
        "diagnostic",
        "direction",
        "submeso",
        "vsubm",
        "grid"
    ],
    "VVEL": [
        "direction",
        "vvel",
        "velocity",
        "grid"
    ],
    "WVEL": [
        "vertical",
        "velocity",
        "wvel"
    ],
    "zooC": [
        "zooc",
        "carbon",
        "zooplankton"
    ],
    "ABIO_ALK_SURF": [
        "alkalinity",
        "abiotic",
        "abio_alk_surf",
        "surface",
        "abio alk surf"
    ],
    "ABIO_CO2STAR": [
        "abio_co2star",
        "abio co2star"
    ],
    "ABIO_D14Catm": [
        "permil",
        "atmospheric",
        "abiotic",
        "abio_d14catm",
        "delta",
        "abio d14catm"
    ],
    "ABIO_D14Cocn": [
        "permil",
        "abio d14cocn",
        "abiotic",
        "delta",
        "oceanic",
        "abio_d14cocn"
    ],
    "ABIO_DCO2STAR": [
        "abio dco2star",
        "abio_dco2star"
    ],
    "ABIO_DIC14": [
        "abio dic14",
        "abio_dic14"
    ],
    "ABIO_DIC": [
        "abio dic",
        "abio_dic"
    ],
    "ABIO_DpCO2": [
        "abio_dpco2",
        "abio dpco2"
    ],
    "ABIO_pCO2SURF": [
        "abio_pco2surf",
        "abio pco2surf"
    ],
    "ABIO_pCO2": [
        "abio pco2",
        "atmospheric",
        "abio_pco2",
        "abiotic",
        "pressure",
        "partial"
    ],
    "ABIO_PH_SURF": [
        "abio_ph_surf",
        "surface",
        "abio ph surf",
        "abiotic"
    ],
    "ADV_3D_SALT": [
        "adv_3d_salt",
        "tendency",
        "adv 3d salt",
        "salt",
        "advection"
    ],
    "ADV_3D_TEMP": [
        "adv 3d temp",
        "tendency",
        "temp",
        "advection",
        "temperature",
        "adv_3d_temp",
        "thermal"
    ],
    "ADVS_ISOP": [
        "advs_isop",
        "vertically",
        "advection",
        "advs isop",
        "induced",
        "integrated",
        "eddy"
    ],
    "ADVS_SUBM": [
        "tendency",
        "submeso",
        "vertically",
        "advection",
        "advs subm",
        "integrated",
        "advs_subm"
    ],
    "ADVS": [
        "tendency",
        "advs",
        "vertically",
        "advection",
        "integrated"
    ],
    "ADVT_ISOP": [
        "advt isop",
        "temp",
        "advt_isop",
        "vertically",
        "advection",
        "induced",
        "temperature",
        "integrated",
        "eddy",
        "thermal"
    ],
    "ADVT_SUBM": [
        "tendency",
        "temp",
        "submeso",
        "vertically",
        "advection",
        "temperature",
        "advt_subm",
        "integrated",
        "advt subm",
        "thermal"
    ],
    "ADVT": [
        "tendency",
        "advt",
        "vertically",
        "advection",
        "integrated"
    ],
    "ADVU": [
        "direction",
        "advection",
        "grid",
        "advu"
    ],
    "ADVV": [
        "direction",
        "advv",
        "grid",
        "advection"
    ],
    "ALK_ALT_CO2_RESTORE_TEND": [
        "alkalinity",
        "tendency",
        "temp",
        "alternative",
        "alk alt co2 restore tend",
        "restoring",
        "temperature",
        "alk_alt_co2_restore_tend",
        "thermal"
    ],
    "ALK_ALT_CO2_RIV_FLUX": [
        "alkalinity",
        "temp",
        "alternative",
        "alk alt co2 riv flux",
        "riverine",
        "temperature",
        "alk_alt_co2_riv_flux",
        "flux",
        "thermal"
    ],
    "ALK_ALT_CO2": [
        "alk_alt_co2",
        "alkalinity",
        "temp",
        "alk alt co2",
        "alternative",
        "temperature",
        "thermal"
    ],
    "ALK_RESTORE_TEND": [
        "alk restore tend",
        "alkalinity",
        "tendency",
        "alk_restore_tend",
        "restoring"
    ],
    "ALK_RIV_FLUX": [
        "alkalinity",
        "alk riv flux",
        "riverine",
        "flux",
        "alk_riv_flux"
    ],
    "ALK": [
        "alkalinity",
        "alk"
    ],
    "AOU": [
        "aou",
        "utilization",
        "apparent"
    ],
    "ATM_ALT_CO2": [
        "temp",
        "atm alt co2",
        "atmospheric",
        "alternative",
        "temperature",
        "atm_alt_co2",
        "thermal"
    ],
    "ATM_BLACK_CARBON_FLUX_CPL": [
        "from",
        "cpl",
        "atm black carbon flux cpl",
        "atm_black_carbon_flux_cpl"
    ],
    "ATM_CO2": [
        "atmospheric",
        "atm_co2",
        "atm co2"
    ],
    "ATM_COARSE_DUST_FLUX_CPL": [
        "cpl",
        "temp",
        "from",
        "temperature",
        "atm_coarse_dust_flux_cpl",
        "atm coarse dust flux cpl",
        "thermal"
    ],
    "ATM_FINE_DUST_FLUX_CPL": [
        "cpl",
        "temp",
        "from",
        "atm_fine_dust_flux_cpl",
        "temperature",
        "atm fine dust flux cpl",
        "thermal"
    ],
    "BSF": [
        "bsf",
        "barotropic",
        "streamfunction",
        "diagnostic"
    ],
    "bSi_form": [
        "total",
        "uptake",
        "bsi_form",
        "bsi form"
    ],
    "bsiToSed": [
        "biogenic",
        "bsitosed",
        "flux",
        "sediments"
    ],
    "CaCO3_FLUX_100m": [
        "flux",
        "caco3_flux_100m",
        "caco3 flux 100m"
    ],
    "CaCO3_form_zint_100m": [
        "caco3_form_zint_100m",
        "temp",
        "formation",
        "integral",
        "vertical",
        "caco3 form zint 100m",
        "total",
        "temperature",
        "thermal"
    ],
    "CaCO3_form_zint": [
        "caco3 form zint",
        "formation",
        "integral",
        "vertical",
        "caco3_form_zint",
        "total"
    ],
    "CaCO3_PROD_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "temperature",
        "production",
        "thermal",
        "caco3_prod_zint_100m",
        "caco3 prod zint 100m"
    ],
    "CaCO3_PROD_zint": [
        "caco3_prod_zint",
        "integral",
        "vertical",
        "production",
        "caco3 prod zint"
    ],
    "CaCO3_REMIN_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "caco3_remin_zint_100m",
        "caco3 remin zint 100m",
        "temperature",
        "remineralization",
        "thermal"
    ],
    "CaCO3_REMIN_zint": [
        "caco3_remin_zint",
        "caco3 remin zint",
        "integral",
        "vertical",
        "remineralization"
    ],
    "calcToSed_ALT_CO2": [
        "temp",
        "alternative",
        "sediments",
        "calctosed alt co2",
        "temperature",
        "calctosed_alt_co2",
        "flux",
        "thermal"
    ],
    "calcToSed": [
        "flux",
        "sediments",
        "calctosed"
    ],
    "CFC11": [
        "cfc11"
    ],
    "CFC12": [
        "cfc12"
    ],
    "CO2STAR_ALT_CO2": [
        "temp",
        "alternative",
        "star",
        "temperature",
        "co2star alt co2",
        "co2star_alt_co2",
        "thermal"
    ],
    "CO2STAR": [
        "co2star",
        "star"
    ],
    "co3_sat_calc": [
        "concentration",
        "temp",
        "saturation",
        "calcite",
        "temperature",
        "co3 sat calc",
        "thermal",
        "co3_sat_calc"
    ],
    "CO3": [
        "concentration",
        "co3",
        "ion",
        "carbonate"
    ],
    "DENITRIF": [
        "denitrification",
        "denitrif"
    ],
    "DIA_IMPVF_PO4": [
        "dia impvf po4",
        "dia_impvf_po4",
        "unknown"
    ],
    "DIA_IMPVF_SALT": [
        "dia impvf salt",
        "face",
        "across",
        "dia_impvf_salt",
        "salt",
        "flux",
        "bottom"
    ],
    "DIA_IMPVF_TEMP": [
        "dia impvf temp",
        "temp",
        "face",
        "across",
        "temperature",
        "thermal",
        "dia_impvf_temp",
        "flux",
        "bottom"
    ],
    "diat_agg_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "aggregation",
        "diat agg zint 100m",
        "diat_agg_zint_100m",
        "temperature",
        "diatom",
        "thermal"
    ],
    "diat_agg_zint": [
        "diat_agg_zint",
        "temp",
        "integral",
        "vertical",
        "aggregation",
        "diat agg zint",
        "temperature",
        "diatom",
        "thermal"
    ],
    "diat_Fe_lim_surf": [
        "temp",
        "diat fe lim surf",
        "limitation",
        "temperature",
        "diatom",
        "surface",
        "diat_fe_lim_surf",
        "thermal"
    ],
    "diatFe": [
        "diatfe",
        "diatom",
        "iron"
    ],
    "diat_light_lim_surf": [
        "diat_light_lim_surf",
        "temp",
        "limitation",
        "light",
        "diatom",
        "temperature",
        "diat light lim surf",
        "surface",
        "thermal"
    ],
    "diat_loss_doc_zint_100m": [
        "loss",
        "temp",
        "integral",
        "vertical",
        "temperature",
        "thermal",
        "diatom",
        "diat loss doc zint 100m",
        "doc",
        "diat_loss_doc_zint_100m"
    ],
    "diat_loss_doc_zint": [
        "loss",
        "temp",
        "integral",
        "vertical",
        "diat loss doc zint",
        "diat_loss_doc_zint",
        "temperature",
        "diatom",
        "doc",
        "thermal"
    ],
    "diat_loss_poc_zint_100m": [
        "diat_loss_poc_zint_100m",
        "poc",
        "loss",
        "temp",
        "integral",
        "vertical",
        "diat loss poc zint 100m",
        "temperature",
        "diatom",
        "thermal"
    ],
    "diat_loss_poc_zint": [
        "poc",
        "loss",
        "diat loss poc zint",
        "integral",
        "diat_loss_poc_zint",
        "vertical",
        "temp",
        "temperature",
        "diatom",
        "thermal"
    ],
    "diat_loss_zint_100m": [
        "loss",
        "temp",
        "integral",
        "vertical",
        "diat_loss_zint_100m",
        "diat loss zint 100m",
        "temperature",
        "diatom",
        "thermal"
    ],
    "diat_loss_zint": [
        "loss",
        "temp",
        "integral",
        "vertical",
        "diat_loss_zint",
        "temperature",
        "thermal",
        "diatom",
        "diat loss zint"
    ],
    "diat_N_lim_surf": [
        "diat_n_lim_surf",
        "temp",
        "limitation",
        "temperature",
        "diatom",
        "surface",
        "thermal",
        "diat n lim surf"
    ],
    "diat_P_lim_surf": [
        "diat p lim surf",
        "temp",
        "limitation",
        "temperature",
        "diatom",
        "surface",
        "diat_p_lim_surf",
        "thermal"
    ],
    "diatP": [
        "diatom",
        "diatp",
        "phosphorus"
    ],
    "diat_Qp": [
        "diat_qp",
        "temp",
        "temperature",
        "diat qp",
        "ratio",
        "diatom",
        "thermal"
    ],
    "diat_SiO3_lim_surf": [
        "diat sio3 lim surf",
        "temp",
        "limitation",
        "diat_sio3_lim_surf",
        "temperature",
        "diatom",
        "surface",
        "thermal"
    ],
    "diatSi": [
        "diatom",
        "diatsi",
        "silicon"
    ],
    "diaz_agg_zint_100m": [
        "diaz agg zint 100m",
        "diazotroph",
        "temp",
        "integral",
        "vertical",
        "aggregation",
        "temperature",
        "diaz_agg_zint_100m",
        "thermal"
    ],
    "diaz_agg_zint": [
        "diazotroph",
        "integral",
        "vertical",
        "diaz agg zint",
        "aggregation",
        "diaz_agg_zint"
    ],
    "diazC": [
        "diazotroph",
        "diazc",
        "carbon"
    ],
    "diaz_Fe_lim_surf": [
        "diaz fe lim surf",
        "diazotroph",
        "diaz_fe_lim_surf",
        "limitation",
        "surface"
    ],
    "diazFe": [
        "diazfe",
        "diazotroph",
        "iron"
    ],
    "diaz_light_lim_surf": [
        "diaz_light_lim_surf",
        "diazotroph",
        "temp",
        "diaz light lim surf",
        "limitation",
        "light",
        "temperature",
        "surface",
        "thermal"
    ],
    "diaz_loss_doc_zint_100m": [
        "diazotroph",
        "loss",
        "temp",
        "diaz loss doc zint 100m",
        "vertical",
        "integral",
        "diaz_loss_doc_zint_100m",
        "temperature",
        "doc",
        "thermal"
    ],
    "diaz_loss_doc_zint": [
        "diazotroph",
        "loss",
        "integral",
        "vertical",
        "diaz loss doc zint",
        "diaz_loss_doc_zint",
        "doc"
    ],
    "diaz_loss_poc_zint_100m": [
        "poc",
        "diazotroph",
        "loss",
        "temp",
        "integral",
        "vertical",
        "temperature",
        "diaz loss poc zint 100m",
        "diaz_loss_poc_zint_100m",
        "thermal"
    ],
    "diaz_loss_poc_zint": [
        "poc",
        "diazotroph",
        "loss",
        "integral",
        "vertical",
        "diaz loss poc zint",
        "diaz_loss_poc_zint"
    ],
    "diaz_loss_zint_100m": [
        "diazotroph",
        "loss",
        "temp",
        "integral",
        "vertical",
        "diaz_loss_zint_100m",
        "temperature",
        "diaz loss zint 100m",
        "thermal"
    ],
    "diaz_loss_zint": [
        "diazotroph",
        "diaz_loss_zint",
        "loss",
        "integral",
        "diaz loss zint",
        "vertical"
    ],
    "diaz_Nfix": [
        "diaz nfix",
        "diazotroph",
        "fixation",
        "diaz_nfix"
    ],
    "diaz_P_lim_surf": [
        "diazotroph",
        "diaz_p_lim_surf",
        "limitation",
        "diaz p lim surf",
        "surface"
    ],
    "diazP": [
        "phosphorus",
        "diazotroph",
        "diazp"
    ],
    "diaz_Qp": [
        "ratio",
        "diazotroph",
        "diaz qp",
        "diaz_qp"
    ],
    "DIC_ALT_CO2_RIV_FLUX": [
        "dic_alt_co2_riv_flux",
        "temp",
        "carbon",
        "inorganic",
        "alternative",
        "dic alt co2 riv flux",
        "riverine",
        "temperature",
        "dissolved",
        "thermal"
    ],
    "DIC_ALT_CO2": [
        "temp",
        "carbon",
        "inorganic",
        "alternative",
        "dic_alt_co2",
        "dic alt co2",
        "temperature",
        "dissolved",
        "thermal"
    ],
    "DIC_RIV_FLUX": [
        "carbon",
        "dic riv flux",
        "inorganic",
        "riverine",
        "dissolved",
        "flux",
        "dic_riv_flux"
    ],
    "DIC": [
        "dissolved",
        "inorganic",
        "carbon",
        "dic"
    ],
    "DOC_prod": [
        "doc_prod",
        "doc",
        "doc prod",
        "production"
    ],
    "DOC_prod_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "doc_prod_zint_100m",
        "doc prod zint 100m",
        "temperature",
        "production",
        "doc",
        "thermal"
    ],
    "DOC_prod_zint": [
        "doc_prod_zint",
        "integral",
        "vertical",
        "doc prod zint",
        "production",
        "doc"
    ],
    "DOC_remin_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "doc remin zint 100m",
        "doc_remin_zint_100m",
        "temperature",
        "doc",
        "remineralization",
        "thermal"
    ],
    "DOC_remin_zint": [
        "integral",
        "doc remin zint",
        "vertical",
        "doc_remin_zint",
        "doc",
        "remineralization"
    ],
    "DOC_RIV_FLUX": [
        "doc riv flux",
        "organic",
        "carbon",
        "doc_riv_flux",
        "riverine",
        "dissolved",
        "flux"
    ],
    "DOCr_remin_zint_100m": [
        "docr_remin_zint_100m",
        "temp",
        "integral",
        "vertical",
        "docr",
        "temperature",
        "docr remin zint 100m",
        "remineralization",
        "thermal"
    ],
    "DOCr_remin_zint": [
        "integral",
        "vertical",
        "docr",
        "docr remin zint",
        "docr_remin_zint",
        "remineralization"
    ],
    "DOCr_RIV_FLUX": [
        "docr_riv_flux",
        "docr riv flux",
        "riverine",
        "flux",
        "doc",
        "refractory"
    ],
    "DOCr": [
        "docr",
        "doc",
        "refractory"
    ],
    "DOC": [
        "dissolved",
        "doc",
        "organic",
        "carbon"
    ],
    "DON_RIV_FLUX": [
        "organic",
        "don_riv_flux",
        "nitrogen",
        "riverine",
        "dissolved",
        "flux",
        "don riv flux"
    ],
    "DONr_RIV_FLUX": [
        "donr riv flux",
        "donr_riv_flux",
        "don",
        "riverine",
        "flux",
        "refractory"
    ],
    "DONr": [
        "don",
        "donr",
        "refractory"
    ],
    "DON": [
        "don",
        "dissolved",
        "nitrogen",
        "organic"
    ],
    "DOP_diat_uptake": [
        "dop_diat_uptake",
        "dop",
        "temp",
        "dop diat uptake",
        "temperature",
        "diatom",
        "uptake",
        "thermal"
    ],
    "DOP_diaz_uptake": [
        "diazotroph",
        "dop",
        "dop_diaz_uptake",
        "dop diaz uptake",
        "uptake"
    ],
    "DOP_remin": [
        "dop_remin",
        "remineralization",
        "dop",
        "dop remin"
    ],
    "DOP_RIV_FLUX": [
        "organic",
        "dop_riv_flux",
        "phosphorus",
        "riverine",
        "dop riv flux",
        "dissolved",
        "flux"
    ],
    "DOPr_remin": [
        "remineralization",
        "dopr_remin",
        "dopr",
        "dopr remin"
    ],
    "DOPr_RIV_FLUX": [
        "dop",
        "dopr riv flux",
        "dopr_riv_flux",
        "riverine",
        "flux",
        "refractory"
    ],
    "DOPr": [
        "dop",
        "dopr",
        "refractory"
    ],
    "DOP_sp_uptake": [
        "dop",
        "dop_sp_uptake",
        "small",
        "dop sp uptake",
        "phyto",
        "uptake"
    ],
    "DOP": [
        "dissolved",
        "phosphorus",
        "dop",
        "organic"
    ],
    "dust_FLUX_IN": [
        "cell",
        "dust",
        "dust_flux_in",
        "dust flux in",
        "temp",
        "temperature",
        "flux",
        "into",
        "thermal"
    ],
    "dust_REMIN": [
        "dust",
        "temp",
        "dust remin",
        "dust_remin",
        "temperature",
        "remineralization",
        "thermal"
    ],
    "dustToSed": [
        "flux",
        "dust",
        "sediments",
        "dusttosed"
    ],
    "ECOSYS_IFRAC": [
        "ice",
        "ecosys",
        "fluxes",
        "ecosys ifrac",
        "for",
        "ecosys_ifrac",
        "fraction"
    ],
    "EVAP_F": [
        "coupler",
        "from",
        "evap f",
        "flux",
        "evap_f",
        "evaporation"
    ],
    "Fefree": [
        "ligand",
        "not",
        "fefree",
        "bound"
    ],
    "Fe_RIV_FLUX": [
        "inorganic",
        "fe_riv_flux",
        "riverine",
        "dissolved",
        "flux",
        "iron",
        "fe riv flux"
    ],
    "Fe": [
        "dissolved",
        "inorganic",
        "iron"
    ],
    "FG_ABIO_DIC14": [
        "fg abio dic14",
        "abiotic",
        "fg_abio_dic14",
        "gas",
        "flux",
        "surface"
    ],
    "FG_ABIO_DIC": [
        "fg abio dic",
        "dic",
        "abiotic",
        "fg_abio_dic",
        "gas",
        "flux",
        "surface"
    ],
    "FRACR_BIN_01": [
        "cell",
        "fracr_bin_01",
        "fracr bin 01",
        "ocean",
        "occupied",
        "fraction",
        "mcog"
    ],
    "FRACR_BIN_02": [
        "cell",
        "fracr bin 02",
        "ocean",
        "fracr_bin_02",
        "occupied",
        "fraction",
        "mcog"
    ],
    "FRACR_BIN_03": [
        "cell",
        "fracr_bin_03",
        "fracr bin 03",
        "ocean",
        "occupied",
        "fraction",
        "mcog"
    ],
    "FRACR_BIN_04": [
        "cell",
        "ocean",
        "fracr_bin_04",
        "occupied",
        "fraction",
        "mcog",
        "fracr bin 04"
    ],
    "FRACR_BIN_05": [
        "cell",
        "fracr bin 05",
        "fracr_bin_05",
        "ocean",
        "occupied",
        "fraction",
        "mcog"
    ],
    "FRACR_BIN_06": [
        "cell",
        "fracr bin 06",
        "ocean",
        "fracr_bin_06",
        "occupied",
        "fraction",
        "mcog"
    ],
    "FvICE_ABIO_DIC14": [
        "ice",
        "fvice_abio_dic14",
        "fvice abio dic14",
        "flux",
        "surface",
        "virtual"
    ],
    "FvICE_ABIO_DIC": [
        "ice",
        "fvice abio dic",
        "fvice_abio_dic",
        "flux",
        "surface",
        "virtual"
    ],
    "FvICE_ALK_ALT_CO2": [
        "alkalinity",
        "temp",
        "alternative",
        "fvice_alk_alt_co2",
        "fvice alk alt co2",
        "temperature",
        "thermal",
        "flux",
        "surface",
        "virtual"
    ],
    "FvICE_DIC_ALT_CO2": [
        "temp",
        "carbon",
        "fvice dic alt co2",
        "inorganic",
        "alternative",
        "fvice_dic_alt_co2",
        "temperature",
        "thermal",
        "dissolved",
        "virtual"
    ],
    "FvPER_ABIO_DIC14": [
        "per",
        "fvper abio dic14",
        "fvper_abio_dic14",
        "flux",
        "surface",
        "virtual"
    ],
    "FvPER_ABIO_DIC": [
        "per",
        "fvper_abio_dic",
        "flux",
        "surface",
        "fvper abio dic",
        "virtual"
    ],
    "FvPER_ALK_ALT_CO2": [
        "fvper_alk_alt_co2",
        "alkalinity",
        "temp",
        "fvper alk alt co2",
        "alternative",
        "temperature",
        "thermal",
        "flux",
        "surface",
        "virtual"
    ],
    "FvPER_DIC_ALT_CO2": [
        "fvper dic alt co2",
        "temp",
        "carbon",
        "inorganic",
        "alternative",
        "temperature",
        "thermal",
        "dissolved",
        "virtual",
        "fvper_dic_alt_co2"
    ],
    "GRADX": [
        "horizontal",
        "direction",
        "grad",
        "grid",
        "gradx",
        "press"
    ],
    "GRADY": [
        "horizontal",
        "direction",
        "grady",
        "grad",
        "grid",
        "press"
    ],
    "graze_diat_doc_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "graze diat doc zint 100m",
        "temperature",
        "thermal",
        "grazing",
        "diatom",
        "doc",
        "graze_diat_doc_zint_100m"
    ],
    "graze_diat_doc_zint": [
        "temp",
        "integral",
        "vertical",
        "graze diat doc zint",
        "temperature",
        "grazing",
        "diatom",
        "doc",
        "graze_diat_doc_zint",
        "thermal"
    ],
    "graze_diat_poc_zint_100m": [
        "poc",
        "temp",
        "graze diat poc zint 100m",
        "graze_diat_poc_zint_100m",
        "vertical",
        "integral",
        "temperature",
        "grazing",
        "diatom",
        "thermal"
    ],
    "graze_diat_poc_zint": [
        "poc",
        "temp",
        "integral",
        "vertical",
        "graze_diat_poc_zint",
        "temperature",
        "graze diat poc zint",
        "grazing",
        "diatom",
        "thermal"
    ],
    "graze_diat_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "grazing",
        "temperature",
        "graze_diat_zint_100m",
        "diatom",
        "graze diat zint 100m",
        "thermal"
    ],
    "graze_diat_zint": [
        "temp",
        "integral",
        "vertical",
        "graze_diat_zint",
        "temperature",
        "thermal",
        "grazing",
        "diatom",
        "graze diat zint"
    ],
    "graze_diat_zoo_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "graze_diat_zoo_zint_100m",
        "zoo",
        "temperature",
        "grazing",
        "diatom",
        "graze diat zoo zint 100m",
        "thermal"
    ],
    "graze_diat_zoo_zint": [
        "graze_diat_zoo_zint",
        "temp",
        "integral",
        "vertical",
        "zoo",
        "graze diat zoo zint",
        "temperature",
        "grazing",
        "diatom",
        "thermal"
    ],
    "graze_diaz_doc_zint_100m": [
        "diazotroph",
        "temp",
        "integral",
        "vertical",
        "graze_diaz_doc_zint_100m",
        "temperature",
        "graze diaz doc zint 100m",
        "grazing",
        "doc",
        "thermal"
    ],
    "graze_diaz_doc_zint": [
        "diazotroph",
        "integral",
        "vertical",
        "graze_diaz_doc_zint",
        "grazing",
        "graze diaz doc zint",
        "doc"
    ],
    "graze_diaz_poc_zint_100m": [
        "poc",
        "diazotroph",
        "temp",
        "integral",
        "vertical",
        "graze diaz poc zint 100m",
        "temperature",
        "grazing",
        "graze_diaz_poc_zint_100m",
        "thermal"
    ],
    "graze_diaz_poc_zint": [
        "graze_diaz_poc_zint",
        "poc",
        "diazotroph",
        "integral",
        "vertical",
        "graze diaz poc zint",
        "grazing"
    ],
    "graze_diaz_zint_100m": [
        "diazotroph",
        "temp",
        "integral",
        "vertical",
        "temperature",
        "graze_diaz_zint_100m",
        "graze diaz zint 100m",
        "grazing",
        "thermal"
    ],
    "graze_diaz_zint": [
        "diazotroph",
        "integral",
        "vertical",
        "graze diaz zint",
        "graze_diaz_zint",
        "grazing"
    ],
    "graze_diaz_zoo_zint_100m": [
        "diazotroph",
        "temp",
        "integral",
        "graze diaz zoo zint 100m",
        "vertical",
        "zoo",
        "temperature",
        "thermal",
        "grazing",
        "graze_diaz_zoo_zint_100m"
    ],
    "graze_diaz_zoo_zint": [
        "diazotroph",
        "integral",
        "vertical",
        "zoo",
        "graze diaz zoo zint",
        "grazing",
        "graze_diaz_zoo_zint"
    ],
    "graze_sp_doc_zint_100m": [
        "graze_sp_doc_zint_100m",
        "temp",
        "vertical",
        "small",
        "phyto",
        "temperature",
        "grazing",
        "doc",
        "graze sp doc zint 100m",
        "thermal"
    ],
    "graze_sp_doc_zint": [
        "graze sp doc zint",
        "vertical",
        "small",
        "phyto",
        "grazing",
        "doc",
        "graze_sp_doc_zint"
    ],
    "graze_sp_poc_zint_100m": [
        "poc",
        "temp",
        "vertical",
        "graze sp poc zint 100m",
        "small",
        "graze_sp_poc_zint_100m",
        "phyto",
        "temperature",
        "grazing",
        "thermal"
    ],
    "graze_sp_poc_zint": [
        "poc",
        "vertical",
        "graze sp poc zint",
        "small",
        "phyto",
        "grazing",
        "graze_sp_poc_zint"
    ],
    "graze_sp_zint_100m": [
        "temp",
        "graze_sp_zint_100m",
        "integral",
        "vertical",
        "small",
        "graze sp zint 100m",
        "phyto",
        "temperature",
        "grazing",
        "thermal"
    ],
    "graze_sp_zint": [
        "graze_sp_zint",
        "integral",
        "vertical",
        "small",
        "phyto",
        "grazing",
        "graze sp zint"
    ],
    "graze_sp_zoo_zint_100m": [
        "temp",
        "vertical",
        "zoo",
        "small",
        "phyto",
        "graze sp zoo zint 100m",
        "temperature",
        "grazing",
        "graze_sp_zoo_zint_100m",
        "thermal"
    ],
    "graze_sp_zoo_zint": [
        "vertical",
        "graze_sp_zoo_zint",
        "zoo",
        "small",
        "graze sp zoo zint",
        "phyto",
        "grazing"
    ],
    "HCO3": [
        "concentration",
        "ion",
        "bicarbonate",
        "hco3"
    ],
    "HDIFE_DIC_ALT_CO2": [
        "horizontal",
        "diffusive",
        "hdife_dic_alt_co2",
        "temp",
        "direction",
        "grid",
        "temperature",
        "flux",
        "hdife dic alt co2",
        "thermal"
    ],
    "HDIFE_DIC": [
        "horizontal",
        "diffusive",
        "dic",
        "hdife_dic",
        "hdife dic",
        "grid",
        "flux"
    ],
    "HDIFE_PO4": [
        "hdife_po4",
        "hdife po4",
        "unknown"
    ],
    "HDIFFU": [
        "horizontal",
        "direction",
        "grid",
        "diffusion",
        "hdiffu"
    ],
    "HDIFFV": [
        "horizontal",
        "direction",
        "hdiffv",
        "diffusion",
        "grid"
    ],
    "HDIFN_DIC_ALT_CO2": [
        "horizontal",
        "diffusive",
        "temp",
        "direction",
        "grid",
        "hdifn dic alt co2",
        "hdifn_dic_alt_co2",
        "temperature",
        "flux",
        "thermal"
    ],
    "HDIFN_DIC": [
        "horizontal",
        "hdifn dic",
        "hdifn_dic",
        "diffusive",
        "dic",
        "grid",
        "flux"
    ],
    "HDIFN_PO4": [
        "hdifn po4",
        "hdifn_po4",
        "unknown"
    ],
    "HDIFT": [
        "tendency",
        "vertically",
        "hdift",
        "integrated",
        "horz",
        "mix"
    ],
    "HMXL_DR2": [
        "layer",
        "squared",
        "hmxl_dr2",
        "hmxl dr2",
        "depth",
        "mixed",
        "density"
    ],
    "HMXL_DR": [
        "layer",
        "hmxl dr",
        "depth",
        "mixed",
        "hmxl_dr",
        "density"
    ],
    "HMXL": [
        "layer",
        "mixed",
        "hmxl",
        "depth"
    ],
    "HOR_DIFF": [
        "hor_diff",
        "horizontal",
        "coefficient",
        "hor diff",
        "diffusion"
    ],
    "IAGE": [
        "ideal",
        "iage",
        "age"
    ],
    "IFRAC": [
        "ice",
        "coupler",
        "ifrac",
        "from",
        "fraction"
    ],
    "insitu_temp": [
        "temp",
        "insitu temp",
        "situ",
        "insitu_temp",
        "temperature",
        "thermal"
    ],
    "IOFF_F": [
        "ice",
        "coupler",
        "from",
        "runoff",
        "ioff_f",
        "flux",
        "ioff f"
    ],
    "ISOP_ADV_TEND_SALT": [
        "isop adv tend salt",
        "tendency",
        "for",
        "advective",
        "induced",
        "isop_adv_tend_salt",
        "eddy"
    ],
    "ISOP_ADV_TEND_TEMP": [
        "tendency",
        "temp",
        "isop adv tend temp",
        "for",
        "advective",
        "induced",
        "isop_adv_tend_temp",
        "temperature",
        "eddy",
        "thermal"
    ],
    "J_DIC_ALT_CO2": [
        "temp",
        "carbon",
        "j dic alt co2",
        "j_dic_alt_co2",
        "inorganic",
        "alternative",
        "source",
        "temperature",
        "dissolved",
        "thermal"
    ],
    "J_DIC": [
        "j_dic",
        "carbon",
        "inorganic",
        "source",
        "j dic",
        "sink",
        "dissolved"
    ],
    "Jint_100m_ALK_ALT_CO2": [
        "jint 100m alk alt co2",
        "alkalinity",
        "jint_100m_alk_alt_co2",
        "temp",
        "alternative",
        "source",
        "term",
        "temperature",
        "sink",
        "thermal"
    ],
    "Jint_100m_DIC_ALT_CO2": [
        "jint 100m dic alt co2",
        "temp",
        "carbon",
        "inorganic",
        "alternative",
        "source",
        "jint_100m_dic_alt_co2",
        "temperature",
        "dissolved",
        "thermal"
    ],
    "Jint_100m_DOCr": [
        "temp",
        "source",
        "term",
        "temperature",
        "sink",
        "jint 100m docr",
        "doc",
        "jint_100m_docr",
        "thermal",
        "refractory"
    ],
    "Jint_ABIO_DIC14": [
        "temp",
        "integral",
        "vertical",
        "source",
        "jint_abio_dic14",
        "term",
        "temperature",
        "sink",
        "jint abio dic14",
        "thermal"
    ],
    "KAPPA_ISOP": [
        "kappa isop",
        "coefficient",
        "kappa_isop",
        "isopycnal",
        "diffusion"
    ],
    "KAPPA_THIC": [
        "coefficient",
        "kappa_thic",
        "kappa thic",
        "diffusion",
        "thickness"
    ],
    "KVMIX": [
        "kvmix",
        "diffusivity",
        "vertical",
        "diabatic",
        "due",
        "tidal"
    ],
    "Lig_deg": [
        "loss",
        "lig deg",
        "from",
        "ligand",
        "lig_deg",
        "bacterial",
        "binding"
    ],
    "Lig_loss": [
        "loss",
        "lig loss",
        "ligand",
        "lig_loss",
        "binding"
    ],
    "Lig_photochem": [
        "loss",
        "from",
        "radiation",
        "lig photochem",
        "lig_photochem",
        "ligand",
        "binding"
    ],
    "Lig_prod": [
        "lig prod",
        "ligand",
        "production",
        "binding",
        "lig_prod"
    ],
    "Lig_scavenge": [
        "scavenging",
        "loss",
        "from",
        "ligand",
        "lig_scavenge",
        "binding",
        "lig scavenge"
    ],
    "Lig": [
        "ligand",
        "lig",
        "binding",
        "iron"
    ],
    "LWDN_F": [
        "heat",
        "lwdn f",
        "coupler",
        "lwdn_f",
        "longwave",
        "from",
        "flux"
    ],
    "LWUP_F": [
        "heat",
        "coupler",
        "longwave",
        "from",
        "lwup f",
        "flux",
        "lwup_f"
    ],
    "MOC": [
        "moc",
        "overturning",
        "circulation",
        "meridional"
    ],
    "NH4": [
        "dissolved",
        "ammonia",
        "nh4"
    ],
    "N_HEAT": [
        "heat",
        "northward",
        "n heat",
        "n_heat",
        "transport"
    ],
    "NHx_SURFACE_EMIS": [
        "nhx_surface_emis",
        "nhx",
        "emission",
        "nhx surface emis",
        "atmosphere"
    ],
    "NITRIF": [
        "nitrification",
        "nitrif"
    ],
    "NO3_RESTORE_TEND": [
        "tendency",
        "nitrate",
        "no3 restore tend",
        "no3_restore_tend",
        "inorganic",
        "dissolved",
        "restoring"
    ],
    "NO3_RIV_FLUX": [
        "no3_riv_flux",
        "nitrate",
        "inorganic",
        "riverine",
        "dissolved",
        "flux",
        "no3 riv flux"
    ],
    "NOx_FLUX": [
        "from",
        "atmosphere",
        "nox_flux",
        "flux",
        "nox",
        "nox flux"
    ],
    "O2_ZMIN_DEPTH": [
        "o2_zmin_depth",
        "o2 zmin depth",
        "minimum",
        "vertical",
        "depth"
    ],
    "O2_ZMIN": [
        "vertical",
        "minimum",
        "o2 zmin",
        "o2_zmin"
    ],
    "pfeToSed": [
        "flux",
        "pfe",
        "sediments",
        "pfetosed"
    ],
    "photoC_diat_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "fixation",
        "photoc_diat_zint_100m",
        "temperature",
        "diatom",
        "photoc diat zint 100m",
        "thermal"
    ],
    "photoC_diat_zint": [
        "temp",
        "integral",
        "vertical",
        "photoc diat zint",
        "fixation",
        "photoc_diat_zint",
        "temperature",
        "diatom",
        "thermal"
    ],
    "photoC_diaz_zint_100m": [
        "photoc diaz zint 100m",
        "diazotroph",
        "temp",
        "integral",
        "vertical",
        "fixation",
        "temperature",
        "photoc_diaz_zint_100m",
        "thermal"
    ],
    "photoC_diaz_zint": [
        "diazotroph",
        "integral",
        "vertical",
        "fixation",
        "photoc_diaz_zint",
        "photoc diaz zint"
    ],
    "photoC_NO3_TOT": [
        "from",
        "fixation",
        "total",
        "photoc no3 tot",
        "photoc_no3_tot"
    ],
    "photoC_NO3_TOT_zint_100m": [
        "photoc_no3_tot_zint_100m",
        "temp",
        "integral",
        "photoc no3 tot zint 100m",
        "from",
        "vertical",
        "fixation",
        "total",
        "temperature",
        "thermal"
    ],
    "photoC_NO3_TOT_zint": [
        "photoc no3 tot zint",
        "temp",
        "integral",
        "vertical",
        "from",
        "fixation",
        "total",
        "photoc_no3_tot_zint",
        "temperature",
        "thermal"
    ],
    "photoC_sp_zint_100m": [
        "temp",
        "integral",
        "vertical",
        "small",
        "fixation",
        "photoc_sp_zint_100m",
        "phyto",
        "temperature",
        "photoc sp zint 100m",
        "thermal"
    ],
    "photoC_sp_zint": [
        "integral",
        "vertical",
        "small",
        "fixation",
        "photoc_sp_zint",
        "phyto",
        "photoc sp zint"
    ],
    "photoC_TOT": [
        "photoc_tot",
        "photoc tot",
        "fixation",
        "total"
    ],
    "photoC_TOT_zint_100m": [
        "photoc_tot_zint_100m",
        "temp",
        "integral",
        "vertical",
        "fixation",
        "total",
        "temperature",
        "thermal",
        "photoc tot zint 100m"
    ],
    "photoC_TOT_zint": [
        "temp",
        "integral",
        "vertical",
        "photoc_tot_zint",
        "fixation",
        "total",
        "photoc tot zint",
        "temperature",
        "thermal"
    ],
    "photoFe_diat": [
        "photofe_diat",
        "uptake",
        "photofe diat",
        "diatom"
    ],
    "photoFe_diaz": [
        "photofe_diaz",
        "uptake",
        "diazotroph",
        "photofe diaz"
    ],
    "photoFe_sp": [
        "small",
        "phyto",
        "photofe sp",
        "uptake",
        "photofe_sp"
    ],
    "photoNH4_diat": [
        "diatom",
        "photonh4_diat",
        "photonh4 diat",
        "uptake"
    ],
    "photoNH4_diaz": [
        "photonh4_diaz",
        "diazotroph",
        "photonh4 diaz",
        "uptake"
    ],
    "photoNH4_sp": [
        "photonh4_sp",
        "photonh4 sp",
        "small",
        "phyto",
        "uptake"
    ],
    "photoNO3_diat": [
        "diatom",
        "photono3 diat",
        "photono3_diat",
        "uptake"
    ],
    "photoNO3_diaz": [
        "photono3_diaz",
        "uptake",
        "diazotroph",
        "photono3 diaz"
    ],
    "photoNO3_sp": [
        "photono3 sp",
        "small",
        "phyto",
        "uptake",
        "photono3_sp"
    ],
    "PH": [
        "surface"
    ],
    "P_iron_FLUX_100m": [
        "p_iron_flux_100m",
        "p iron flux 100m",
        "flux"
    ],
    "P_iron_REMIN": [
        "p_iron_remin",
        "p iron remin",
        "remineralization"
    ],
    "PO4_diat_uptake": [
        "temp",
        "po4_diat_uptake",
        "temperature",
        "diatom",
        "uptake",
        "po4 diat uptake",
        "thermal"
    ],
    "PO4_diaz_uptake": [
        "uptake",
        "po4_diaz_uptake",
        "po4 diaz uptake",
        "diazotroph"
    ],
    "PO4_RESTORE_TEND": [
        "tendency",
        "po4_restore_tend",
        "po4 restore tend",
        "inorganic",
        "restoring",
        "dissolved",
        "phosphate"
    ],
    "PO4_RIV_FLUX": [
        "po4_riv_flux",
        "inorganic",
        "dissolved",
        "riverine",
        "po4 riv flux",
        "phosphate",
        "flux"
    ],
    "PO4_sp_uptake": [
        "po4_sp_uptake",
        "small",
        "po4 sp uptake",
        "phyto",
        "uptake"
    ],
    "POC_FLUX_100m": [
        "flux",
        "poc",
        "poc flux 100m",
        "poc_flux_100m"
    ],
    "POC_FLUX_IN": [
        "cell",
        "poc",
        "poc flux in",
        "flux",
        "into",
        "poc_flux_in"
    ],
    "POC_PROD": [
        "poc",
        "poc_prod",
        "poc prod",
        "production"
    ],
    "POC_PROD_zint_100m": [
        "poc",
        "poc_prod_zint_100m",
        "temp",
        "integral",
        "vertical",
        "temperature",
        "production",
        "poc prod zint 100m",
        "thermal"
    ],
    "POC_PROD_zint": [
        "poc",
        "integral",
        "vertical",
        "poc_prod_zint",
        "poc prod zint",
        "production"
    ],
    "POC_REMIN_DIC_zint_100m": [
        "poc",
        "poc_remin_dic_zint_100m",
        "temp",
        "integral",
        "vertical",
        "routed",
        "temperature",
        "remineralization",
        "thermal",
        "poc remin dic zint 100m"
    ],
    "POC_REMIN_DIC_zint": [
        "poc",
        "poc_remin_dic_zint",
        "integral",
        "vertical",
        "routed",
        "remineralization",
        "poc remin dic zint"
    ],
    "POC_REMIN_DOCr_zint_100m": [
        "poc",
        "temp",
        "integral",
        "vertical",
        "poc_remin_docr_zint_100m",
        "routed",
        "poc remin docr zint 100m",
        "temperature",
        "remineralization",
        "thermal"
    ],
    "POC_REMIN_DOCr_zint": [
        "poc",
        "integral",
        "vertical",
        "routed",
        "poc remin docr zint",
        "remineralization",
        "poc_remin_docr_zint"
    ],
    "pocToSed": [
        "poc",
        "flux",
        "poctosed",
        "sediments"
    ],
    "ponToSed": [
        "burial",
        "nitrogen",
        "sediments",
        "flux",
        "pontosed"
    ],
    "POP_FLUX_100m": [
        "pop_flux_100m",
        "pop flux 100m",
        "pop",
        "flux"
    ],
    "POP_FLUX_IN": [
        "cell",
        "pop flux in",
        "pop_flux_in",
        "pop",
        "flux",
        "into"
    ],
    "POP_PROD": [
        "pop prod",
        "pop_prod",
        "pop",
        "production"
    ],
    "POP_REMIN_DOPr": [
        "dopr",
        "pop",
        "pop_remin_dopr",
        "routed",
        "remineralization",
        "pop remin dopr"
    ],
    "POP_REMIN_PO4": [
        "pop_remin_po4",
        "pop",
        "routed",
        "pop remin po4",
        "remineralization"
    ],
    "popToSed": [
        "phosphorus",
        "flux",
        "sediments",
        "poptosed"
    ],
    "PREC_F": [
        "precipitation",
        "cpl",
        "rainfall",
        "from",
        "prec_f",
        "flux",
        "prec f",
        "rain"
    ],
    "PV": [
        "vorticity",
        "potential"
    ],
    "QFLUX": [
        "heat",
        "qflux",
        "ocean",
        "due",
        "internal",
        "flux"
    ],
    "QSW_3D": [
        "heat",
        "short",
        "wave",
        "solar",
        "qsw_3d",
        "flux",
        "qsw 3d"
    ],
    "QSW_BIN_01": [
        "net",
        "bin",
        "qsw bin 01",
        "qsw_bin_01",
        "shortwave",
        "mcog",
        "into"
    ],
    "QSW_BIN_02": [
        "net",
        "bin",
        "qsw bin 02",
        "shortwave",
        "mcog",
        "into",
        "qsw_bin_02"
    ],
    "QSW_BIN_03": [
        "net",
        "bin",
        "qsw bin 03",
        "qsw_bin_03",
        "shortwave",
        "mcog",
        "into"
    ],
    "QSW_BIN_04": [
        "net",
        "bin",
        "qsw bin 04",
        "shortwave",
        "mcog",
        "into",
        "qsw_bin_04"
    ],
    "QSW_BIN_05": [
        "net",
        "bin",
        "qsw bin 05",
        "qsw_bin_05",
        "shortwave",
        "mcog",
        "into"
    ],
    "QSW_BIN_06": [
        "net",
        "bin",
        "qsw bin 06",
        "qsw_bin_06",
        "shortwave",
        "mcog",
        "into"
    ],
    "Redi_TEND_SALT": [
        "tendency",
        "for",
        "redi",
        "redi_tend_salt",
        "salt",
        "redi tend salt"
    ],
    "Redi_TEND_TEMP": [
        "redi_tend_temp",
        "tendency",
        "temp",
        "for",
        "redi",
        "redi tend temp",
        "temperature",
        "thermal"
    ],
    "RESID_T": [
        "surface",
        "resid t",
        "free",
        "flux",
        "resid_t",
        "residual"
    ],
    "RF_TEND_SALT": [
        "tendency",
        "rf_tend_salt",
        "robert",
        "for",
        "salt",
        "filter",
        "rf tend salt"
    ],
    "RF_TEND_TEMP": [
        "rf_tend_temp",
        "tendency",
        "temp",
        "robert",
        "for",
        "temperature",
        "rf tend temp",
        "filter",
        "thermal"
    ],
    "RHO": [
        "rho",
        "situ",
        "density"
    ],
    "RHO_VINT": [
        "integral",
        "vertical",
        "rho_vint",
        "situ",
        "rho vint",
        "density"
    ],
    "ROFF_F": [
        "coupler",
        "from",
        "runoff",
        "roff f",
        "roff_f",
        "flux"
    ],
    "SEAICE_BLACK_CARBON_FLUX_CPL": [
        "from",
        "cpl",
        "seaice_black_carbon_flux_cpl",
        "seaice black carbon flux cpl"
    ],
    "SEAICE_DUST_FLUX_CPL": [
        "cpl",
        "temp",
        "seaice dust flux cpl",
        "from",
        "temperature",
        "seaice_dust_flux_cpl",
        "thermal"
    ],
    "SedDenitrif": [
        "seddenitrif",
        "sediments",
        "loss",
        "nitrogen"
    ],
    "SF6_ATM_PRESS": [
        "fluxes",
        "atmospheric",
        "for",
        "pressure",
        "sf6 atm press",
        "sf6_atm_press"
    ],
    "SF6_IFRAC": [
        "ice",
        "fluxes",
        "sf6 ifrac",
        "for",
        "sf6_ifrac",
        "fraction"
    ],
    "SF6": [
        "sf6"
    ],
    "SF6_XKW": [
        "sf6 xkw",
        "fluxes",
        "xkw",
        "sf6_xkw",
        "for"
    ],
    "S_FLUX_EXCH_INTRF": [
        "vertical",
        "salt",
        "across",
        "s flux exch intrf",
        "flux",
        "s_flux_exch_intrf",
        "upper"
    ],
    "S_FLUX_ROFF_VSF_SRF": [
        "s flux roff vsf srf",
        "salt",
        "flux",
        "s_flux_roff_vsf_srf",
        "surface",
        "virtual"
    ],
    "SFWF": [
        "sfwf",
        "formulation",
        "salt",
        "flux",
        "virtual"
    ],
    "SHF_QSW": [
        "shf qsw",
        "heat",
        "shf_qsw",
        "short",
        "wave",
        "solar",
        "flux"
    ],
    "SHF": [
        "heat",
        "including",
        "total",
        "shf",
        "flux",
        "surface"
    ],
    "SiO2_FLUX_100m": [
        "flux",
        "sio2 flux 100m",
        "sio2_flux_100m"
    ],
    "SiO2_PROD": [
        "sio2 prod",
        "sio2_prod",
        "production"
    ],
    "SiO3_RESTORE_TEND": [
        "tendency",
        "inorganic",
        "dissolved",
        "silicate",
        "sio3 restore tend",
        "restoring",
        "sio3_restore_tend"
    ],
    "SiO3_RIV_FLUX": [
        "sio3 riv flux",
        "sio3_riv_flux",
        "inorganic",
        "riverine",
        "silicate",
        "dissolved",
        "flux"
    ],
    "SiO3": [
        "dissolved",
        "sio3",
        "inorganic",
        "silicate"
    ],
    "sp_agg_zint_100m": [
        "sp agg zint 100m",
        "temp",
        "integral",
        "sp_agg_zint_100m",
        "vertical",
        "small",
        "aggregation",
        "phyto",
        "temperature",
        "thermal"
    ],
    "sp_agg_zint": [
        "integral",
        "vertical",
        "small",
        "aggregation",
        "sp_agg_zint",
        "phyto",
        "sp agg zint"
    ],
    "spCaCO3": [
        "spcaco3",
        "small",
        "phyto"
    ],
    "sp_Fe_lim_surf": [
        "sp fe lim surf",
        "small",
        "limitation",
        "sp_fe_lim_surf",
        "phyto",
        "surface"
    ],
    "spFe": [
        "phyto",
        "small",
        "spfe",
        "iron"
    ],
    "sp_light_lim_surf": [
        "temp",
        "small",
        "sp_light_lim_surf",
        "limitation",
        "light",
        "phyto",
        "temperature",
        "surface",
        "sp light lim surf",
        "thermal"
    ],
    "sp_loss_doc_zint_100m": [
        "sp_loss_doc_zint_100m",
        "loss",
        "temp",
        "sp loss doc zint 100m",
        "vertical",
        "small",
        "phyto",
        "temperature",
        "doc",
        "thermal"
    ],
    "sp_loss_doc_zint": [
        "loss",
        "vertical",
        "small",
        "sp_loss_doc_zint",
        "sp loss doc zint",
        "phyto",
        "doc"
    ],
    "sp_loss_poc_zint_100m": [
        "poc",
        "loss",
        "temp",
        "sp_loss_poc_zint_100m",
        "vertical",
        "small",
        "phyto",
        "temperature",
        "sp loss poc zint 100m",
        "thermal"
    ],
    "sp_loss_poc_zint": [
        "poc",
        "loss",
        "sp loss poc zint",
        "vertical",
        "small",
        "sp_loss_poc_zint",
        "phyto"
    ],
    "sp_loss_zint_100m": [
        "loss",
        "temp",
        "integral",
        "vertical",
        "sp loss zint 100m",
        "small",
        "sp_loss_zint_100m",
        "phyto",
        "temperature",
        "thermal"
    ],
    "sp_loss_zint": [
        "loss",
        "integral",
        "vertical",
        "small",
        "phyto",
        "sp_loss_zint",
        "sp loss zint"
    ],
    "sp_N_lim_surf": [
        "sp n lim surf",
        "sp_n_lim_surf",
        "small",
        "limitation",
        "phyto",
        "surface"
    ],
    "sp_P_lim_surf": [
        "sp p lim surf",
        "sp_p_lim_surf",
        "small",
        "limitation",
        "phyto",
        "surface"
    ],
    "spP": [
        "spp",
        "phosphorus",
        "small",
        "phyto"
    ],
    "sp_Qp": [
        "sp_qp",
        "small",
        "phyto",
        "ratio",
        "sp qp"
    ],
    "SSH": [
        "surface",
        "ssh",
        "sea",
        "height"
    ],
    "SSS2": [
        "sss2",
        "surface",
        "salinity",
        "sea"
    ],
    "STF_ABIO_DIC14": [
        "stf abio dic14",
        "stf_abio_dic14",
        "excludes",
        "term",
        "fvice",
        "flux",
        "surface"
    ],
    "STF_ABIO_DIC": [
        "stf abio dic",
        "stf_abio_dic",
        "excludes",
        "term",
        "fvice",
        "flux",
        "surface"
    ],
    "STF_ALK_ALT_CO2": [
        "stf_alk_alt_co2",
        "alkalinity",
        "stf alk alt co2",
        "temp",
        "alternative",
        "excludes",
        "temperature",
        "flux",
        "surface",
        "thermal"
    ],
    "STF_ALK": [
        "stf alk",
        "alkalinity",
        "excludes",
        "stf_alk",
        "fvice",
        "flux",
        "surface"
    ],
    "STF_SF6": [
        "stf sf6",
        "excludes",
        "term",
        "fvice",
        "flux",
        "surface",
        "stf_sf6"
    ],
    "SUBM_ADV_TEND_SALT": [
        "tendency",
        "submeso",
        "for",
        "salt",
        "subm_adv_tend_salt",
        "subm adv tend salt",
        "advective"
    ],
    "SUBM_ADV_TEND_TEMP": [
        "tendency",
        "temp",
        "submeso",
        "for",
        "temperature",
        "subm adv tend temp",
        "advective",
        "thermal",
        "subm_adv_tend_temp"
    ],
    "SU": [
        "velocity",
        "direction",
        "vertically",
        "integrated",
        "grid"
    ],
    "SV": [
        "velocity",
        "direction",
        "vertically",
        "integrated",
        "grid"
    ],
    "TAUX2": [
        "direction",
        "grid",
        "windstress",
        "taux2"
    ],
    "TAUY2": [
        "direction",
        "grid",
        "tauy2",
        "windstress"
    ],
    "TEMP2": [
        "temp2",
        "temperature",
        "thermal",
        "temp"
    ],
    "TEND_SALT": [
        "tendency",
        "salt",
        "tend_salt",
        "tend salt",
        "thickness",
        "weighted"
    ],
    "TEND_TEMP": [
        "tendency",
        "temp",
        "tend temp",
        "temperature",
        "thermal",
        "thickness",
        "weighted",
        "tend_temp"
    ],
    "tend_zint_100m_ALK_ALT_CO2": [
        "tend zint 100m alk alt co2",
        "alkalinity",
        "tendency",
        "temp",
        "integral",
        "vertical",
        "alternative",
        "temperature",
        "tend_zint_100m_alk_alt_co2",
        "thermal"
    ],
    "tend_zint_100m_DOCr": [
        "tendency",
        "temp",
        "integral",
        "vertical",
        "tend zint 100m docr",
        "temperature",
        "doc",
        "tend_zint_100m_docr",
        "thermal",
        "refractory"
    ],
    "tend_zint_100m_SiO3": [
        "tendency",
        "temp",
        "vertical",
        "inorganic",
        "tend zint 100m sio3",
        "tend_zint_100m_sio3",
        "silicate",
        "temperature",
        "dissolved",
        "thermal"
    ],
    "T_FLUX_EXCH_INTRF": [
        "t flux exch intrf",
        "temp",
        "vertical",
        "across",
        "t_flux_exch_intrf",
        "temperature",
        "upper",
        "flux",
        "thermal"
    ],
    "TIDAL_DIFF": [
        "tidal diff",
        "tidal_diff",
        "jayne",
        "diffusion",
        "tidal"
    ],
    "TMXL_DR": [
        "layer",
        "minimum",
        "density",
        "depth",
        "mixed",
        "tmxl dr",
        "tmxl_dr"
    ],
    "UE_DIC_ALT_CO2": [
        "ue dic alt co2",
        "temp",
        "direction",
        "ue_dic_alt_co2",
        "temperature",
        "flux",
        "grid",
        "thermal"
    ],
    "UE_DIC": [
        "direction",
        "ue dic",
        "dic",
        "flux",
        "grid",
        "ue_dic"
    ],
    "UE_PO4": [
        "ue_po4",
        "ue po4",
        "unknown"
    ],
    "UES": [
        "ues",
        "direction",
        "salt",
        "grid",
        "flux"
    ],
    "UET": [
        "heat",
        "direction",
        "flux",
        "grid",
        "uet"
    ],
    "UVEL2": [
        "direction",
        "velocity",
        "uvel2",
        "grid"
    ],
    "VDC_T": [
        "diffusivity",
        "temp",
        "vdc t",
        "vertical",
        "diabatic",
        "total",
        "vdc_t"
    ],
    "VDIFFU": [
        "direction",
        "vertical",
        "vdiffu",
        "diffusion",
        "grid"
    ],
    "VDIFFV": [
        "vertical",
        "direction",
        "vdiffv",
        "diffusion",
        "grid"
    ],
    "VN_DIC_ALT_CO2": [
        "vn_dic_alt_co2",
        "temp",
        "direction",
        "flux",
        "temperature",
        "vn dic alt co2",
        "grid",
        "thermal"
    ],
    "VN_DIC": [
        "direction",
        "dic",
        "grid",
        "flux",
        "vn_dic",
        "vn dic"
    ],
    "VN_PO4": [
        "vn po4",
        "vn_po4",
        "unknown"
    ],
    "VNS": [
        "direction",
        "salt",
        "grid",
        "flux",
        "vns"
    ],
    "VNT_ISOP": [
        "heat",
        "tendency",
        "temp",
        "vnt isop",
        "grid",
        "temperature",
        "vnt_isop",
        "flux",
        "thermal",
        "dir"
    ],
    "VNT": [
        "heat",
        "direction",
        "vnt",
        "grid",
        "flux"
    ],
    "VVEL2": [
        "direction",
        "vvel2",
        "velocity",
        "grid"
    ],
    "WISOP": [
        "velocity",
        "diagnostic",
        "vertical",
        "wisop",
        "bolus"
    ],
    "WSUBM": [
        "velocity",
        "diagnostic",
        "vertical",
        "submeso",
        "wsubm"
    ],
    "WT_DIC_ALT_CO2": [
        "top",
        "temp",
        "wt_dic_alt_co2",
        "wt dic alt co2",
        "face",
        "across",
        "temperature",
        "flux",
        "thermal"
    ],
    "WT_DIC": [
        "top",
        "temp",
        "wt_dic",
        "face",
        "dic",
        "across",
        "temperature",
        "wt dic",
        "flux",
        "thermal"
    ],
    "WT_PO4": [
        "wt po4",
        "temp",
        "temperature",
        "wt_po4",
        "thermal",
        "unknown"
    ],
    "WTS": [
        "top",
        "face",
        "across",
        "salt",
        "flux",
        "wts"
    ],
    "WTT": [
        "top",
        "heat",
        "wtt",
        "face",
        "across",
        "flux"
    ],
    "XMXL_DR": [
        "layer",
        "xmxl dr",
        "xmxl_dr",
        "maximum",
        "depth",
        "mixed",
        "density"
    ],
    "XMXL": [
        "layer",
        "maximum",
        "depth",
        "mixed",
        "xmxl"
    ],
    "zoo_loss_doc_zint_100m": [
        "loss",
        "temp",
        "integral",
        "vertical",
        "zooplankton",
        "temperature",
        "zoo loss doc zint 100m",
        "doc",
        "zoo_loss_doc_zint_100m",
        "thermal"
    ],
    "zoo_loss_doc_zint": [
        "zoo loss doc zint",
        "loss",
        "integral",
        "vertical",
        "zooplankton",
        "zoo_loss_doc_zint",
        "doc"
    ],
    "zoo_loss_poc_zint_100m": [
        "poc",
        "loss",
        "temp",
        "integral",
        "vertical",
        "zoo loss poc zint 100m",
        "zooplankton",
        "temperature",
        "zoo_loss_poc_zint_100m",
        "thermal"
    ],
    "zoo_loss_poc_zint": [
        "poc",
        "loss",
        "zoo_loss_poc_zint",
        "integral",
        "vertical",
        "zoo loss poc zint",
        "zooplankton"
    ],
    "zoo_loss_zint_100m": [
        "loss",
        "temp",
        "integral",
        "vertical",
        "zoo loss zint 100m",
        "zooplankton",
        "zoo_loss_zint_100m",
        "temperature",
        "thermal"
    ],
    "zoo_loss_zint": [
        "loss",
        "zoo loss zint",
        "integral",
        "vertical",
        "zooplankton",
        "zoo_loss_zint"
    ],
    "CaCO3_ALT_CO2_FLUX_IN": [
        "caco3 alt co2 flux in",
        "cell",
        "temp",
        "alternative",
        "caco3_alt_co2_flux_in",
        "temperature",
        "flux",
        "into",
        "thermal"
    ],
    "CaCO3_ALT_CO2_REMIN": [
        "caco3 alt co2 remin",
        "temp",
        "alternative",
        "caco3_alt_co2_remin",
        "temperature",
        "remineralization",
        "thermal"
    ],
    "CaCO3_FLUX_IN": [
        "cell",
        "caco3 flux in",
        "caco3_flux_in",
        "flux",
        "into"
    ],
    "CaCO3_form": [
        "total",
        "caco3 form",
        "formation",
        "caco3_form"
    ],
    "CaCO3_PROD": [
        "caco3_prod",
        "caco3 prod",
        "production"
    ],
    "CaCO3_REMIN": [
        "caco3 remin",
        "remineralization",
        "caco3_remin"
    ],
    "DIA_IMPVF_DIC_ALT_CO2": [
        "dia impvf dic alt co2",
        "temp",
        "from",
        "dia_impvf_dic_alt_co2",
        "face",
        "across",
        "temperature",
        "thermal",
        "flux",
        "bottom"
    ],
    "DIA_IMPVF_DIC": [
        "dia impvf dic",
        "face",
        "dic",
        "across",
        "dia_impvf_dic",
        "flux",
        "bottom"
    ],
    "DIA_IMPVF_DOCr": [
        "dia impvf docr",
        "docr",
        "face",
        "across",
        "dia_impvf_docr",
        "flux",
        "bottom"
    ],
    "DOC_remin": [
        "doc",
        "doc_remin",
        "remineralization",
        "doc remin"
    ],
    "DOCr_remin": [
        "docr",
        "docr remin",
        "docr_remin",
        "remineralization"
    ],
    "DON_remin": [
        "don remin",
        "don_remin",
        "remineralization",
        "don"
    ],
    "DONr_remin": [
        "donr",
        "donr remin",
        "remineralization",
        "donr_remin"
    ],
    "graze_auto_TOT": [
        "graze_auto_tot",
        "autotroph",
        "graze auto tot",
        "total",
        "grazing"
    ],
    "HDIFB_DIC_ALT_CO2": [
        "hdifb dic alt co2",
        "horizontal",
        "diffusive",
        "temp",
        "across",
        "temperature",
        "thermal",
        "hdifb_dic_alt_co2",
        "flux",
        "bottom"
    ],
    "HDIFB_DIC": [
        "hdifb_dic",
        "horizontal",
        "diffusive",
        "dic",
        "across",
        "flux",
        "hdifb dic"
    ],
    "HDIFB_DOCr": [
        "horizontal",
        "diffusive",
        "docr",
        "across",
        "hdifb docr",
        "hdifb_docr",
        "flux"
    ],
    "HDIFE_DOCr": [
        "horizontal",
        "diffusive",
        "docr",
        "hdife docr",
        "hdife_docr",
        "grid",
        "flux"
    ],
    "HDIFN_DOCr": [
        "horizontal",
        "diffusive",
        "docr",
        "hdifn docr",
        "grid",
        "flux",
        "hdifn_docr"
    ],
    "J_ALK_ALT_CO2": [
        "alkalinity",
        "temp",
        "alternative",
        "source",
        "j alk alt co2",
        "term",
        "j_alk_alt_co2",
        "temperature",
        "sink",
        "thermal"
    ],
    "J_NO3": [
        "nitrate",
        "inorganic",
        "source",
        "sink",
        "dissolved",
        "j no3",
        "j_no3"
    ],
    "J_SiO3": [
        "inorganic",
        "source",
        "j sio3",
        "silicate",
        "sink",
        "j_sio3",
        "dissolved"
    ],
    "KPP_SRC_DIC_ALT_CO2": [
        "kpp",
        "tendency",
        "local",
        "non",
        "temp",
        "from",
        "temperature",
        "kpp src dic alt co2",
        "kpp_src_dic_alt_co2",
        "thermal"
    ],
    "KPP_SRC_DIC": [
        "kpp",
        "tendency",
        "non",
        "from",
        "dic",
        "kpp_src_dic",
        "kpp src dic"
    ],
    "POC_REMIN_DIC": [
        "poc",
        "poc remin dic",
        "dic",
        "poc_remin_dic",
        "routed",
        "remineralization"
    ],
    "POC_REMIN_DOCr": [
        "poc",
        "docr",
        "poc remin docr",
        "poc_remin_docr",
        "routed",
        "remineralization"
    ],
    "PON_REMIN_DONr": [
        "donr",
        "pon remin donr",
        "pon",
        "routed",
        "pon_remin_donr",
        "remineralization"
    ],
    "PON_REMIN_NH4": [
        "pon",
        "routed",
        "pon remin nh4",
        "pon_remin_nh4",
        "remineralization"
    ],
    "RF_TEND_DIC_ALT_CO2": [
        "tendency",
        "temp",
        "robert",
        "for",
        "rf_tend_dic_alt_co2",
        "temperature",
        "rf tend dic alt co2",
        "filter",
        "thermal"
    ],
    "RF_TEND_DIC": [
        "tendency",
        "robert",
        "for",
        "dic",
        "rf_tend_dic",
        "filter",
        "rf tend dic"
    ],
    "RF_TEND_DOCr": [
        "tendency",
        "docr",
        "robert",
        "for",
        "rf_tend_docr",
        "filter",
        "rf tend docr"
    ],
    "RF_TEND_DOC": [
        "tendency",
        "rf_tend_doc",
        "robert",
        "for",
        "doc",
        "rf tend doc",
        "filter"
    ],
    "RF_TEND_Fe": [
        "tendency",
        "robert",
        "for",
        "rf_tend_fe",
        "filter",
        "rf tend fe"
    ],
    "RF_TEND_O2": [
        "rf tend o2",
        "tendency",
        "rf_tend_o2",
        "robert",
        "for",
        "filter"
    ],
    "TEND_DIC_ALT_CO2": [
        "tendency",
        "temp",
        "tend dic alt co2",
        "temperature",
        "thermal",
        "tend_dic_alt_co2",
        "thickness",
        "weighted"
    ],
    "TEND_DIC": [
        "tend_dic",
        "tendency",
        "dic",
        "tend dic",
        "thickness",
        "weighted"
    ],
    "TEND_DOCr": [
        "tendency",
        "tend docr",
        "docr",
        "tend_docr",
        "thickness",
        "weighted"
    ],
    "TEND_DOC": [
        "tendency",
        "tend doc",
        "tend_doc",
        "doc",
        "thickness",
        "weighted"
    ],
    "TEND_Fe": [
        "tendency",
        "tend_fe",
        "thickness",
        "weighted",
        "tend fe"
    ],
    "TEND_O2": [
        "tendency",
        "tend_o2",
        "tend o2",
        "thickness",
        "weighted"
    ],
    "UE_DOCr": [
        "ue docr",
        "docr",
        "direction",
        "grid",
        "ue_docr",
        "flux"
    ],
    "VN_DOCr": [
        "docr",
        "direction",
        "vn_docr",
        "flux",
        "grid",
        "vn docr"
    ],
    "WT_DOCr": [
        "top",
        "temp",
        "docr",
        "face",
        "across",
        "wt docr",
        "temperature",
        "flux",
        "wt_docr",
        "thermal"
    ],
    "RIVER_DISCHARGE_OVER_LAND_LIQ": [
        "river_discharge_over_land_liq",
        "flow",
        "river",
        "liq",
        "river discharge over land liq",
        "mosart",
        "basin"
    ],
    "TOTAL_DISCHARGE_TO_OCEAN_LIQ": [
        "total discharge to ocean liq",
        "total_discharge_to_ocean_liq",
        "total",
        "discharge",
        "ocean",
        "mosart",
        "into"
    ],
    "DIRECT_DISCHARGE_TO_OCEAN_ICE": [
        "direct discharge to ocean ice",
        "temp",
        "direct_discharge_to_ocean_ice",
        "discharge",
        "ocean",
        "direct",
        "temperature",
        "mosart",
        "into",
        "thermal"
    ],
    "DIRECT_DISCHARGE_TO_OCEAN_LIQ": [
        "direct discharge to ocean liq",
        "temp",
        "direct_discharge_to_ocean_liq",
        "discharge",
        "ocean",
        "direct",
        "temperature",
        "mosart",
        "into",
        "thermal"
    ],
    "RIVER_DISCHARGE_OVER_LAND_ICE": [
        "ice",
        "flow",
        "river",
        "river discharge over land ice",
        "mosart",
        "basin",
        "river_discharge_over_land_ice"
    ],
    "TOTAL_DISCHARGE_TO_OCEAN_ICE": [
        "total",
        "discharge",
        "ocean",
        "total discharge to ocean ice",
        "mosart",
        "total_discharge_to_ocean_ice",
        "into"
    ]
}

def get_cesm_variable(keyword_or_name):
    """
    Get CESM variable info by keyword or variable name
    Enhanced to handle both exact matches and keyword searches
    """
    # Direct name lookup (exact match)
    if keyword_or_name.upper() in CESM_VARIABLES:
        return CESM_VARIABLES[keyword_or_name.upper()]
    
    # Keyword search
    keyword_lower = keyword_or_name.lower()
    for var_name, var_info in CESM_VARIABLES.items():
        # Check if keyword matches variable keywords
        if var_name in VARIABLE_KEYWORDS:
            for keyword in VARIABLE_KEYWORDS[var_name]:
                if keyword in keyword_lower:
                    return var_info
        
        # Check if keyword matches variable names/descriptions
        if (keyword_lower in var_info["cesm_name"].lower() or 
            keyword_lower in var_info["description"].lower() or
            keyword_lower in var_info["standard_name"].lower()):
            return var_info
    
    return None

def get_cesm_component(component_name):
    """
    Get CESM component info by component name or abbreviation
    """
    component_lower = component_name.lower()
    
    # Direct lookup
    if component_lower in CESM_COMPONENTS:
        return CESM_COMPONENTS[component_lower]
    
    # Search by abbreviation or full name
    for comp_key, comp_info in CESM_COMPONENTS.items():
        if (component_lower == comp_info["abbreviation"].lower() or
            component_lower in comp_info["full_name"].lower()):
            return comp_info
    
    return None

def create_variable_node(variable_info, dataset_id):
    """
    Create a standardized variable node for the knowledge graph
    """
    return {
        "variable_id": f"VAR_{variable_info['cesm_name']}_{dataset_id}",
        "cesm_name": variable_info["cesm_name"],
        "standard_name": variable_info["standard_name"],
        "units": variable_info["units"],
        "description": variable_info["description"],
        "domain": variable_info["domain"],
        "component": variable_info.get("component", "unknown"),
        "source_dataset": dataset_id
    }

def create_component_node(component_info, dataset_id):
    """
    Create a standardized component node for the knowledge graph
    """
    return {
        "component_id": f"COMP_{component_info['abbreviation']}_{dataset_id}",
        "component_name": component_info["abbreviation"],
        "full_name": component_info["full_name"],
        "description": component_info["description"],
        "domain": component_info["domain"],
        "source_dataset": dataset_id
    }

# Summary statistics
print(f"CESM Variables loaded: {len(CESM_VARIABLES)} variables across {len(CESM_COMPONENTS)} components")
component_counts = {}
for var in CESM_VARIABLES.values():
    comp = var.get('component', 'unknown')
    component_counts[comp] = component_counts.get(comp, 0) + 1

print("Variables per component:")
for comp, count in sorted(component_counts.items()):
    comp_info = CESM_COMPONENTS.get(comp, {})
    comp_name = comp_info.get('abbreviation', comp.upper())
    print(f"  {comp_name}: {count} variables")
