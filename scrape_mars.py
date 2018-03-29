from bs4 import BeautifulSoup as bs
import requests
from selenium import webdriver
from splinter import Browser
import time

import json
import tweepy
import apikeys #PLEASE IMPORT YOUR OWN TWITTER KEY HERE!!!!
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

def scrape():
    url = 'https://mars.nasa.gov/news/'
    browser = webdriver.Chrome('chromedriver.exe')

    browser.get(url)
    html = browser.page_source

    soup = bs(html, 'html.parser')
    browser.close()

    soup_li = soup.find_all('li', class_='slide')
    list_of_titles = []
    list_of_paragraphs = []

    for eachslide in soup_li:
        one_title = eachslide.find('div', class_='content_title').text
        one_paragraph = eachslide.find('div', class_='article_teaser_body').text
        list_of_titles.append(one_title)
        list_of_paragraphs.append(one_paragraph)

    ######## NEWS TITLE AND PARAGRAPHS LOCATION #########
    news_title = list_of_titles[0]
    news_p = list_of_paragraphs[0]
    #####################################################

    splint_browser = Browser('chrome', executable_path='chromedriver.exe',
                    headless=False)

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    splint_browser.visit(url)

    splint_browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(2)
    splint_browser.click_link_by_partial_text('more info')
    html = splint_browser.html
    soup = bs(html, 'html.parser')
    splint_browser.quit()

    image_src = soup.find_all('figure', class_='lede')
    for each in image_src:
    ######### FEATURED IMAGE URL #########################
        featured_image_url = 'https://www.jpl.nasa.gov'+each.a['href']

    #######################################################

    # Twitter API Keys
    consumer_key = apikeys.TWITTER_CONSUMER_KEY
    consumer_secret = apikeys.TWITTER_CONSUMER_SECRET
    access_token = apikeys.TWITTER_ACCESS_TOKEN
    access_token_secret = apikeys.TWITTER_ACCESS_TOKEN_SECRET

    # Setup Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

    public_tweets = api.user_timeline('marswxreport', count = 5)
    for tweet in public_tweets:
    ########## MARS WEATHER TWEET ##########################
        if (("hPa" in tweet['text']) and ("Sol" in tweet['text'])):
            mars_weather = tweet['text']
            break

    #########################################################

    url_tables = 'https://space-facts.com/mars/'
    tables = pd.read_html(url_tables)
    table_df = pd.DataFrame(tables[0])
    table_df = table_df.rename(columns={0:"planet_profile", 1:"mars_data"})
    table_df = table_df.set_index('planet_profile')
    ############### TABLE WITH MARS INFORMATION ###############
    table_html = pd.DataFrame.to_html(table_df)

    ###########################################################

    splint_browser = Browser('chrome', executable_path='chromedriver.exe',
                    headless=False)
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    splint_browser.visit(url)

    hemisphere_list = []
    html = splint_browser.html
    soup = bs(html, 'html.parser')
    findHemisphere = soup.find_all('div', class_='item')

    for each in findHemisphere:
        hemisphere_list.append(each.h3.text)
        
    splint_browser.quit()

    hemisphere_image = []

    for eachHemi in hemisphere_list:

        splint_browser = Browser('chrome', executable_path='chromedriver.exe',
                    headless=False)
        splint_browser.visit(url)
        time.sleep(2)
        splint_browser.click_link_by_partial_text(eachHemi)

        time.sleep(2)
        splint_browser.click_link_by_text('Sample')
        #Line 23
        splint_browser.windows.current = splint_browser.windows[1]
        #Line 24
        html = splint_browser.html
        soup = bs(html, 'html.parser')
        splint_browser.quit()
        #Line 25
        hemi_image = soup.body.find('img')['src']
        
        hemisphere_image.append(hemi_image)

    ################ HEMISPHERES IMAGES - URL ########################
    title_image_url = []
    title_image_tuple = zip(hemisphere_list, hemisphere_image)

    for each in title_image_tuple:
        temp_dict = {}
        temp_dict['title'] = each[0]
        temp_dict['img_url'] = each[1]
        title_image_url.append(temp_dict)
    ###################################################################

    mars_dict = {'News_Title': news_title, 'News_Paragraph': news_p, 'Featured_Image':
    featured_image_url, 'Mars_Weather': mars_weather, 'Mars_Info': table_html,
    'Hemisphere_Images': title_image_url}

    return mars_dict






