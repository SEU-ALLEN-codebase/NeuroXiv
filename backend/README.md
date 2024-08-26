# neuron_analysis

This repo contains basic functions and data APIs for neuron morphology analysis.

demo requests:
curl -X GET localhost:5000/search
curl -X GET localhost:5000/search -H "Content-Type: application/json" --data '{"id_list":["AIBS_18869_6854_x10735_y2978_CCFv3", "SEU_17786_x_28605.1_y_15774.9_z_3799.25_CCFv3"]}'
curl -X GET localhost:5000/search -H "Content-Type: application/json" --data '{"criteria":{"celltype":["MOp","MOs"]}}'
curl -X GET localhost:5000/neurons/SEU_17786_x_28605.1_y_15774.9_z_3799.25_CCFv3
