import datetime


market_cutting = {
     # -------- DAY --------
    "SRIDEVI_DAY_OP":   100,
    "SRIDEVI_DAY_CL":   100,
    "TIME_BAZAR_DAY_OP": 100,
    "TIME_BAZAR_DAY_CL": 100,
    "MADHUR_DAY_OP": 100,
    "MADHUR_DAY_CL": 100,
    "MILAN_DAY_OP": 100,
    "MILAN_DAY_CL": 100,
    "RAJDHANI_DAY_OP": 100,
    "RAJDHANI_DAY_CL": 100,
    "SUPREME_DAY_OP":100,
    "SUPREME_DAY_CL": 100,
    "KALYAN_DAY_OP": 100,
    "KALYAN_DAY_CL": 100,

    # -------- NIGHT --------
    "SRIDEVI_NIGHT_OP": 100,
    "SRIDEVI_NIGHT_CL": 100,
    "MADHUR_NIGHT_OP": 100,
    "MADHUR_NIGHT_CL": 100,
    "SUPREME_NIGHT_OP": 100,
    "SUPREME_NIGHT_CL": 100,
    "MILAN_NIGHT_OP": 100,
    "MILAN_NIGHT_CL": 100,
    "RAJDHANI_NIGHT_OP": 100,
    "RAJDHANI_NIGHT_CL": 100,
    "KALYAN_NIGHT_OP": 100,
    "KALYAN_NIGHT_CL": 100,
    "MAIN_BAZAR_NIGHT_OP": 100,
    "MAIN_BAZAR_NIGHT_CL": 100,
}

# =================================================
# MARKET TIME TABLE
# =================================================
MARKET_TIME_TABLE = {

    # -------- DAY --------
    "SRIDEVI_DAY_OP":   (datetime.time(1, 0), 6, datetime.time(11, 41)),
    "SRIDEVI_DAY_CL":   (datetime.time(11, 43), 6, datetime.time(12, 41)),

    "TIME_BAZAR_DAY_OP": (datetime.time(1, 0), 5, datetime.time(13, 8)),
    "TIME_BAZAR_DAY_CL": (datetime.time(13, 7), 5, datetime.time(14, 8)),

    "MADHUR_DAY_OP": (datetime.time(1, 0), 6, datetime.time(13, 37)),
    "MADHUR_DAY_CL": (datetime.time(13, 39), 6, datetime.time(14, 37)),

    "MILAN_DAY_OP": (datetime.time(1, 0), 5, datetime.time(15, 8)),
    "MILAN_DAY_CL": (datetime.time(15, 10), 5, datetime.time(17, 8)),

    "RAJDHANI_DAY_OP": (datetime.time(1, 0), 5, datetime.time(15, 17)),
    "RAJDHANI_DAY_CL": (datetime.time(15, 20), 5, datetime.time(17, 17)),

    "SUPREME_DAY_OP": (datetime.time(1, 0), 6, datetime.time(15, 38)),
    "SUPREME_DAY_CL": (datetime.time(15, 41), 6, datetime.time(17, 38)),

    "KALYAN_DAY_OP": (datetime.time(1, 0), 5, datetime.time(16, 10)),
    "KALYAN_DAY_CL": (datetime.time(16, 10), 5, datetime.time(18, 10)),

    # -------- NIGHT --------
    "SRIDEVI_NIGHT_OP": (datetime.time(17, 0), 6, datetime.time(19, 19)),
    "SRIDEVI_NIGHT_CL": (datetime.time(19, 21), 6, datetime.time(20, 19)),
    #"SRIDEVI_NIGHT_CL": (datetime.time(19, 21), 6, datetime.time(6, 13)),


    "MADHUR_NIGHT_OP": (datetime.time(17, 0), 5, datetime.time(20, 37)),
    "MADHUR_NIGHT_CL": (datetime.time(20, 41), 5, datetime.time(22, 37)),

    "SUPREME_NIGHT_OP": (datetime.time(17, 45), 6, datetime.time(20, 48)),
    "SUPREME_NIGHT_CL": (datetime.time(20, 51), 6, datetime.time(22, 48)),

    "MILAN_NIGHT_OP": (datetime.time(17, 45), 5, datetime.time(21, 6)),
    "MILAN_NIGHT_CL": (datetime.time(21, 8), 5, datetime.time(23, 6)),

    "RAJDHANI_NIGHT_OP": (datetime.time(17, 45), 4, datetime.time(21, 38)),
    "RAJDHANI_NIGHT_CL": (datetime.time(21, 42), 4, datetime.time(23, 49)),

    "KALYAN_NIGHT_OP": (datetime.time(18, 15), 4, datetime.time(21, 40)),
    "KALYAN_NIGHT_CL": (datetime.time(21, 42), 4, datetime.time(23, 40)),

    "MAIN_BAZAR_NIGHT_OP": (datetime.time(1, 0), 4, datetime.time(21, 59)),
    "MAIN_BAZAR_NIGHT_CL": (datetime.time(22, 1), 4, datetime.time(0, 7)),
}
main_num_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9','0','10', '11', '12', '13', '14', 
                 '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', 
                 '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', 
                 '41','42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', 
                 '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', 
                 '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', 
            '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', 
            '94', '95', '96', '97', '98', '99','00', '01', '02', '03', '04', '05', '06', '07','08', '09',
            '000', '100', '110', '111', '112', '113', '114', '115', '116', '117', '118', '119',
            '120', '122', '123', '124', '125', '126', '127', '128', '129', '130', '133', '134', 
            '135', '136', '137', '138', '139', '140', '144', '145', '146', '147', '148', '149', 
            '150', '155', '156', '157', '158', '159', '160', '166', '167', '168', '169', '170', 
            '177', '178', '179', '180', '188', '189', '190', '199', '200', '220', '222', '223', 
            '224', '225', '226', '227', '228', '229', '230', '233', '234', '235', '236', '237', 
            '238', '239', '240', '244', '245', '246', '247', '248', '249', '250', '255', '256', 
            '257', '258', '259', '260', '266', '267', '268', '269', '270', '277', '278', '279', 
            '280', '288', '289', '290', '299', '300', '330', '333', '334', '335', '336', '337', 
            '338', '339', '340', '344', '345', '346', '347', '348', '349', '350', '355', '356', 
            '357', '358', '359', '360', '366', '367', '368', '369', '370', '377', '378', '379', 
            '380', '388', '389', '390', '399', '400', '440', '444', '445', '446', '447', '448', 
            '449', '450', '455', '456', '457', '458', '459', '460', '466', '467', '468', '469', 
            '470', '477', '478', '479', '480', '488', '489', '490', '499', '500', '550', '555', 
            '556', '557', '558', '559', '560', '566', '567', '568', '569', '570', '577', '578', 
            '579', '580', '588', '589', '590', '599', '600', '660', '666', '667', '668', '669', 
            '670', '677', '678', '679', '680', '688', '689', '690', '699', '700', '770', '777', 
            '778', '779', '780', '788', '789', '790', '799', '800', '880', '888', '889', '890', 
            '899', '900', '990', '999']

WIN_RATES = {
    "ANK": 9.5,
    "Jodi" : 95,
    "SP" : 150,
    "DP" : 300,
    "TP" : 600,
    "FS" : 10000,
    "HS" : 1000
}





