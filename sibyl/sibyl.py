from slackbot.bot import respond_to, listen_to
from slackbot.utils import download_file, create_tmp_file
import numpy as np
import matplotlib.pyplot as plt
import lightkurve as lk
from astroquery.mast import Catalogs
from astropy.io import ascii
import pandas as pd
import re

@respond_to('hi|hello', re.IGNORECASE)
def hi(message):
    message.reply('G\'day')

@respond_to('quicklook (.*) (Kepler|K2|TESS) (long|short)', re.IGNORECASE)
def quicklook(message, star_id, mission=('Kepler', 'K2', 'TESS'), cadence='long'):
    message.react('+1')
    try:
        lc = lk.search_lightcurvefile(star_id, mission=mission, cadence=cadence).download_all().stitch().remove_nans()

        _, ax = plt.subplots(2,1, figsize=[10,10], constrained_layout=True)
        lc.plot(ax=ax[0])
        lc.to_periodogram().plot(ax=ax[1])
        with create_tmp_file() as tmp_file:
            plt.savefig(tmp_file + '.png', bbox_inches='tight')
            message.channel.upload_file(star_id, tmp_file + '.png')
    except:
        message.reply('I could not resolve your query. ')

@respond_to('lightcurve (.*) (Kepler|K2|TESS) (long|short)', re.IGNORECASE)
def plot_lightcurve(message, star_id, mission=('Kepler', 'K2', 'TESS'), cadence=None):
    message.react('+1')

    if cadence is None:
        lc = lk.search_lightcurvefile(star_id, mission=mission).download_all().stitch().remove_nans()
    else:
        lc = lk.search_lightcurvefile(star_id, mission=mission, cadence=cadence).download_all().stitch().remove_nans()

    _, ax = plt.subplots(figsize=[10,5], constrained_layout=True)
    lc.plot(ax=ax)
    with create_tmp_file() as tmp_file:
        plt.savefig(tmp_file + '.png', bbox_inches='tight')
        message.channel.upload_file(star_id, tmp_file + '.png')

@respond_to('query (.*) (.*)', re.IGNORECASE)
def query(message, catalog, star_id):
    message.react('+1')
    try:
        catalogData = Catalogs.query_object(star_id, catalog=catalog, radius=0.01)
        if catalog == 'Gaia':
            df = catalogData['source_id', 'ra', 'dec','parallax','parallax_error','phot_g_mean_mag','distance'].to_pandas()
            response = "I have found *{}* stars within a 0.01 degree radius of {}. \n".format(len(catalogData), star_id)
            response += "```" + df.to_string() + "```"
        elif catalog == 'TIC':
            df = catalogData['ID','ra','dec','HIP','TYC','UCAC','TWOMASS','SDSS','ALLWISE','GAIA','APASS','KIC'].to_pandas()
            response = "I have found *{}* stars within a 0.01 degree radius of {}. \n".format(len(catalogData), star_id)
            response += "```" + df.to_string() + "```"
    except:
        response = "Could not resolve query"

    message.reply(response, in_thread=True)