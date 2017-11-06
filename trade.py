#!/usr/bin/env python

import krakenex
import os
import json
import sys
import time


def btfy(text):
    if "EQuery" in text:
        return text.replace("EQuery:", "Kraken Error (Query): ")
    elif "EGeneral" in text:
        return text.replace("EGeneral:", "Kraken Error (General): ")
    elif "EService" in text:
        return text.replace("EService:", "Kraken Error (Service): ")
    elif "EAPI" in text:
        return text.replace("EAPI:", "Kraken Error (API): ")
    elif "EOrder" in text:
        return text.replace("EOrder:", "Kraken Error (Order): ")
    elif "EFunding" in text:
        return text.replace("EFunding:", "Kraken Error (Funding): ")

    return text


def trim_zeros(value_to_trim):
    if isinstance(value_to_trim, float):
        return ('%.8f' % value_to_trim).rstrip('0').rstrip('.')
    elif isinstance(value_to_trim, str):
        str_list = value_to_trim.split(" ")
        for i in range(len(str_list)):
            old_str = str_list[i]
            if old_str.replace(".", "").isdigit():
                new_str = str(('%.8f' % float(old_str)).rstrip('0').rstrip('.'))
                str_list[i] = new_str
        return " ".join(str_list)
    else:
        return value_to_trim


def trade_buy_sell(config, monnaie, taux, gain,quantite):

    # configure api
    kraken = krakenex.API()
    kraken.load_key('kraken.key')

    # prepare request
    req_data = {'docalcs': 'true'}

    res_balance = kraken.query_private("Balance")

    if res_balance["error"]:
        print(btfy(res_balance["error"][0]))

    # print(res_balance)

    res_orders = kraken.query_private("OpenOrders")

    req_data = dict()

    cpt = 0
    investit = 0

    while cpt > -1 :

        cpt += 15

        req_data["pair"] = "X" + monnaie + "Z" + config["trade_to_currency"]
        res_data = kraken.query_public("Ticker", req_data)

        # print(res_data)


        # on test si cela nous renvoie une erreur
        if(len(res_data["error"]) == 0):

            last_trade_price = trim_zeros(res_data["result"][req_data["pair"]]["c"][0])

            print(str(cpt) + " secondes," + monnaie + ": " + last_trade_price + " " + config["trade_to_currency"])


            if((float(last_trade_price) <= float(taux)) & (investit == 0)):
                investit = 1
                print("Investissement à un taux de " + str(float(last_trade_price)))
                investissement = float(last_trade_price)


            # Si la personne a investit on calcule les gains potentiels

            if(investit == 1):

                # Si la personne génère des gains
                if(float(last_trade_price) >= investissement):
                    # Calcule du gain
                    gaingagné = (float(last_trade_price) - investissement) * float(quantite)

                    # Si le gain est atteint
                    if(gaingagné >= float(gain)):

                        print("Gain gagné : " + str(gain))
                        cpt = -1
                    else:
                        print("Gain insufisant : " + str(gaingagné))


            time.sleep(15)
        else:
            print(btfy(res_data["error"]))
            cpt = -1








def main():
    # Ouverture du json contenant les inforamtions
    if os.path.isfile("config.json"):
    	with open("config.json") as config_file:
    		config = json.load(config_file)

    else:
        exit("No configuration file 'config.json' found")


    # Récupération des paramètres placés au programme

    monnaie = ""

    i = 0
    while i < len(sys.argv):

        # Définition de la monnaie
        if(sys.argv[i] == "-m"):
            monnaie = sys.argv[i+1]
            i += 1

        # Choix du seuil d'investissement    
        if(sys.argv[i] == "-i"):
            investissement = sys.argv[i+1]

        # First action (buy / sell)
        if(sys.argv[i] == "-fa"):
            firstaction = sys.argv[i+1]
            taux = sys.argv[i+2]
            i += 2


        # Second action (buy / sell)
        if(sys.argv[i] == "-sa"):
            secondaction = sys.argv[i+1]
            gain = sys.argv[i+2]
            i += 2

        # Quantité de monnaie (ex : 100 Ripples)
        if(sys.argv[i] == "-q"):
            quantite = sys.argv[i+1]
            i += 1

        i += 1


    # Si la personne n'a pas spécifié de monnaie


    if(monnaie == ""):

        # Affichage de toutes les monnaies

        print("\nVoici les monnaies disponible : ")

        for coin, url in config["coin_charts"].items():

            print(" - " + coin + "   (" + url + ")")
        print()

    # Monnaie connue
    else:
        trade_buy_sell(config,monnaie,taux,gain,quantite)








if __name__ == "__main__":
    main()


