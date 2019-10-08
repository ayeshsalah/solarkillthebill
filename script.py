from flask import Flask, render_template, request, redirect, flash, send_from_directory
import os

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        existing = ""
        new_construction = ""
        area = float(request.form.get('areaInput'))
        load_kw = float(request.form.get('loadKW'))
        load_hp = float(request.form.get('loadHP'))
        units = float(request.form.get('unitsInput'))
        if request.form.get('outputPerDay'):
            output_per_day = float(request.form.get('outputPerDay'))
        else:
            output_per_day = 4
        billing_type = request.form.get('billingOptionsRadios')
        north_coordinates = request.form.get('northCoordinate')
        east_coordinates = request.form.get('eastCoordinates')
        building_height = request.form.get('heightInput')
        floors = request.form.get('floorsInput')
        construction_type = request.form.get('optionsRadios')
        if construction_type == "existing":
            existing = "checked"
        if construction_type == "new construction":
            new_construction = "checked"

        contracted_load = (0.746 * load_hp) + load_kw

        contracted_load = round(contracted_load * 2) / 2 # rounding to nearest 0.5

        cca = 0
        ccb = 0
        if billing_type == "Commercial":
            if 0 < contracted_load > 1:
                cca = contracted_load * 80
        else:
            if 0 < contracted_load > 1:
                cca = 1 * 60
                ccb = (contracted_load - 1) * 70
            else:
                cca = contracted_load * 60

        fuel_cess = round(units * 0.29, 2)
        slab_rates = set_slab_rates(billing_type)
        slabs = calculate_slabs(units, slab_rates, billing_type)
        tax = round(((slabs[0] + slabs[1] + slabs[2] + slabs[3] + slabs[4] + slabs[5]) * 9)/100, 2)
        recommended_value1 = round((units - 100)/120, 1)
        # recommended_value2 = round(contracted_load * 0.75, 2)
        recommended_value2 = round(area/70, 1)
        # print(recommended_value1, recommended_value2, recommended_value3)
        recommended_value = min([recommended_value1, recommended_value2, contracted_load]) 
        net_bill = round(cca+ccb+slabs[0] + slabs[1] + slabs[2] + slabs[3] + slabs[4] + slabs[5]+fuel_cess+tax, 2)

        expected_units_montly = output_per_day * recommended_value * 30
        expected_units_yearly = round(output_per_day * recommended_value * 365, 2)
        expected_units_quater_century = round(expected_units_yearly * 25, 2)
        units_after = units - expected_units_montly 

        carbon_dioxide_mitigated = int((expected_units_quater_century/1000) * 0.82)
        teak_trees = int(expected_units_quater_century/762)
 
        slabs_after = calculate_slabs(units_after, slab_rates, billing_type)
        fuel_cess_after = round(units_after * 0.15, 2)
        tax_after = round(((slabs_after[0] + slabs_after[1] + slabs_after[2] + slabs_after[3] + slabs_after[4] + slabs_after[5]) * 6)/100, 2)
        net_bill_after = round(cca+ccb+slabs_after[0] + slabs_after[1] + slabs_after[2] + slabs_after[3] + slabs_after[4] + slabs_after[5]+fuel_cess_after+tax_after, 2)
        # print((0.746 * load_hp) + load_kw)
        # print(contracted_load)
        # print(slabs[0], slabs[1], slabs[2], slabs[3], slabs[4], slabs[5])
        # print(tax)
        # print(recommended_value)
        # print(area, load_kw, load_hp, units, billing_type, output_per_day,
        # north_coordinates, east_coordinates, building_height, floors, construction_type)

        return render_template('submitted.html', area=area, load_kw=load_kw, load_hp=load_hp, units=units,
                               output=output_per_day, billing_type=billing_type, north=north_coordinates,
                               east=east_coordinates, height=building_height, floors=floors, existing=existing,
                               newconstruction=new_construction, cca=cca, ccb=ccb, slab1=slabs[0], slab2=slabs[1], slab3=slabs[2], slab4=slabs[3], slab5=slabs[4], slab6=slabs[5],
                               fuelcess=fuel_cess, tax=tax, netbill=net_bill, contracted_load=round(contracted_load,1), killthebill = recommended_value, 
                               slab1after=slabs_after[0], slab2after=slabs_after[1], slab3after=slabs_after[2], slab4after=slabs_after[3], slab5after=slabs_after[4], 
                               slab6after=slabs_after[5], fuelcessafter=fuel_cess_after, taxafter=tax_after, netbillafter=net_bill_after, savings = round(net_bill-net_bill_after, 2),
                               slab1rate=slab_rates[0], slab2rate=slab_rates[1], slab3rate=slab_rates[2], slab4rate=slab_rates[3], slab5rate=slab_rates[4], slab6rate=slab_rates[5],
                               rv1=recommended_value1, rv2=recommended_value2, expected_units_yearly=expected_units_yearly, expected_units_quater_century=expected_units_quater_century,
                               carbon_dioxide_mitigated=carbon_dioxide_mitigated, teak_trees=teak_trees)
    else:
        return render_template('home.html')

def set_slab_rates(billing_type):
    if billing_type=="Urban":
        slab1_rate = 3.75
        slab2_rate = 5.20
        slab3_rate = 6.75
        slab4_rate = 7.80
        slab5_rate = 7.80
        slab6_rate = 7.80
    elif billing_type == "Rural":
        slab1_rate = 3.65
        slab2_rate = 4.90
        slab3_rate = 6.45
        slab4_rate = 7.30
        slab5_rate = 7.30
        slab6_rate = 7.30
    elif billing_type=="Commercial":
        slab1_rate = 8.00
        slab2_rate = 9.00
        slab3_rate = 0
        slab4_rate = 0
        slab5_rate = 0
        slab6_rate = 0
    return([slab1_rate, slab2_rate, slab3_rate, slab4_rate, slab5_rate, slab6_rate])

def calculate_slabs(units, slab_rates, billing_type):
    if billing_type == "Urban" or billing_type == "Rural":
        slab1 = 0
        slab2 = 0
        slab3 = 0
        slab4 = 0
        slab5 = 0
        slab6 = 0
        if units > 30:
            slab1 = 30 * slab_rates[0]
            units = units - 30
            if units > 70:
                slab2 = 70 * slab_rates[1]
                units = units - 70
                if units > 100:
                    slab3 = 100 * slab_rates[2]
                    units = units - 100
                    if units > 100:
                        slab4 = 100 * slab_rates[3]
                        units = units - 100
                        if units > 100:
                            slab5 = 100 * slab_rates[4]
                            units = units - 100
                            if units > 0:
                                slab6 = units * slab_rates[5]
                        else:
                            slab5 = units * slab_rates[4]
                    else:
                        slab4 = units * slab_rates[3]
                else:
                    slab3 = units * slab_rates[2]
            else:
                slab2 = units * slab_rates[1]
        else:
            slab1 = units * slab_rates[0]
        return([round(slab1, 2), round(slab2, 2), round(slab3, 2), round(slab4, 2), round(slab5,2), round(slab6,2)])
    else:
        slab1 = 0
        slab2 = 0
        if units > 50:
            slab1 = 50 * slab_rates[0]
            units = units - 50
            if units > 0:
                slab2 = units * slab_rates[1]
        else:
            slab1 = units * slab_rates[0]
        return([round(slab1, 2), round(slab2, 2), 0, 0, 0, 0])

if __name__ == '__main__':
    app.run(debug=True)
