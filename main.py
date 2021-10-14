import os
import pandas as pd
import numpy as np
import data_loader
import opt_fut_calc

from datetime import date
########################################################################################################################
debug = True
strike_price = 435
vol_rate = 0.12
rf_kzt = 0.08
rf_usd = 0.0001
packs_per_stock = 1000
basis = 365
########################################################################################################################
filename = "USDKZT_TOM_11.10.2021.xls"
xls_filename = pd.read_excel(filename)
xls_filename.to_csv(r'./USDKZT_TOM_11.10.2021.csv', index=None, header=True)

if __name__ == '__main__':
    pd_df_1 = data_loader.Data("USDKZT_TOM_11.10.2021.csv")
    date_np, er_11_np = pd_df_1.create_df()
    diff_days = []
    date_array = date_np.tolist()            # dates array from numpy
    er_11_array = er_11_np.tolist()

    if not debug:
        while True:
            try:
                print("Current data base starts from " + date_np[0] + " and finishes at " + date_np[len(date_np)-1])
                start_date = input('Enter the start date (format: dd.mm.yy): \n')
                finish_date = input('Enter the finish date (format: dd.mm.yy): \n')
                new_date_array = date_np[date_array.index(start_date):date_array.index(finish_date)+1]
                new_er_11_array = er_11_np[date_array.index(start_date):date_array.index(finish_date)+1]
                break

            except ValueError:
                print("Check dates, not found in the data base... Try again...\n")
    else:  # test dates
        start_date = "01.10.20"
        finish_date = "15.10.20"
        new_date_array = date_np[date_array.index(start_date):date_array.index(finish_date)+1]
        new_er_11_array = er_11_np[date_array.index(start_date):date_array.index(finish_date)+1]

    for i, element in enumerate(new_date_array):
        if i < (len(new_date_array)-1):
            diff = pd_df_1.difference_day(element, new_date_array[len(new_date_array)-1])
            diff_days.append(diff.days)
        else:
            break

    new_date_array = np.delete(new_date_array, -1)
    new_er_11_array = np.delete(new_er_11_array, -1)

    new_date_array = np.array(new_date_array).reshape(-1, 1)
    new_er_11_array = np.array(new_er_11_array).reshape(-1, 1)
    diff_days = np.array(diff_days).reshape(-1, 1)

    merged_array = np.hstack((new_date_array, new_er_11_array, diff_days))

    calc_1 = opt_fut_calc.Calc(strike_price, vol_rate, rf_kzt, rf_usd, packs_per_stock, basis)

    array_fwd_price = np.zeros((len(new_date_array), 1))
    array_d_one = np.zeros((len(new_date_array), 1))
    array_d_two = np.zeros((len(new_date_array), 1))
    array_N_d_one = np.zeros((len(new_date_array), 1))
    array_N_d_two = np.zeros((len(new_date_array), 1))
    array_option_c = np.zeros((len(new_date_array), 1))
    array_N_d_one_minus = np.zeros((len(new_date_array), 1))
    array_N_d_two_minus = np.zeros((len(new_date_array), 1))
    array_option_p = np.zeros((len(new_date_array), 1))
    array_s_b_s = np.zeros((len(new_date_array), 1))
    array_s_b_m = np.zeros((len(new_date_array), 1))
    array_accum = np.zeros((len(new_date_array), 1))

   # print(merged_array)

    for i, row in enumerate(merged_array):

        fwd_price = calc_1.fwd_price(float(row[1]), int(row[2]))
        d_one = calc_1.d_one(fwd_price, int(row[2]))
        d_two = calc_1.d_two(d_one, int(row[2]))
        N_d_one = calc_1.normal_d(d_one)
        N_d_two = calc_1.normal_d(d_two)
        opt_c = calc_1.option_call(int(row[2]), fwd_price, N_d_one, N_d_two)
        N_d_one_minus = calc_1.normal_d(-d_one)
        N_d_two_minus = calc_1.normal_d(-d_two)
        opt_p = calc_1.option_put(int(row[2]), fwd_price, N_d_one_minus, N_d_two_minus)

        array_fwd_price[i] = fwd_price
        array_d_one[i] = d_one
        array_d_two[i] = d_two
        array_N_d_one[i] = N_d_one
        array_N_d_two[i] = N_d_two
        array_option_c[i] = opt_c
        array_N_d_one_minus[i] = N_d_one_minus
        array_N_d_two_minus[i] = N_d_two_minus
        array_option_p[i] = opt_p

        if i == 0:
            tmp_s = N_d_one*calc_1.stock_size
        else:
            tmp_s = calc_1.sbs(array_N_d_one[i-1], array_N_d_one[i])
        array_s_b_s[i] = tmp_s

        tmp_m = calc_1.sbm(tmp_s, fwd_price)
        array_s_b_m[i] = tmp_m

        if i == 0:
            tmp_accum = tmp_m
        else:
            tmp_accum = calc_1.accum(array_s_b_m[i - 1], array_s_b_m[i])
        array_accum[i] = tmp_accum

    #print(array_fwd_price)
    merged_array = np.hstack((merged_array, array_fwd_price, array_d_one, array_d_two, array_N_d_one,
                              array_N_d_two, array_N_d_one_minus, array_N_d_two_minus, array_option_c,
                              array_option_p, array_s_b_s, array_s_b_m, array_accum))
    #print(merged_array)
    #print(merged_array.shape)
    #print(merged_array.shape)

    result_df = pd.DataFrame(merged_array, columns=['Date', 'Stock Price', 'Day Period', 'Forward Price',
                                                    'd_1', 'd_2', 'N(d_1)', 'N(d_2)', 'N(-d_1)', 'N(-d_2)',
                                                    'Option Call', 'Option Put', 'Sell/Buy Stocks', 'Sell/Buy Stock KZT', 'Accumulated KZT'])

    #print(result_df)
    saved_name = os.path.splitext(pd_df_1.file_name)[0]
    #print(saved_name)
    result_df.to_csv(saved_name + "_analyzed.csv", index=False)
    result_df.to_excel(saved_name + "_analyzed.xlsx", index=False)
