import streamlit as st
import requests

st.set_page_config("Salah Input 2024", "📢")

st.header("CEK SALAH INPUT PILPRES 2024")
st.subheader("Aplikasi ini akan menunjukkan TPS yang memiliki total suara capres lebih besar dari total suara sah juga yang memiliki total suara capres lebih dari 300")
st.write("*Aplikasi ini tidak menghitung TPS yang belum melakukan submit serta TPS yang belum memasukkan data DPT*")

def checkTPSSus(kelurahan_ID):
  TPS_req = requests.get('https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp' + kelurahan_ID + '.json')
  List_TPS = TPS_req.json()

  TPS_table = List_TPS['table']
  TPS_done = [data for data in TPS_table if '100025' in TPS_table[data]]

  TPS_sus = []
  def AppendTPSSus(TPS_ID,TPS_data,fault):
    newData = {}
    newData['No_TPS'] = TPS_ID[-3:]
    newData['Kesalahan'] = fault
    newData['Suara_Sah'] = TPS_data['administrasi']['suara_sah']
    newData['Suara_Total_Paslon'] = sum([i for i in TPS_data['chart'].values() if i])
    newData['Suara_01'] = TPS_data['chart']['100025']
    newData['Suara_02'] = TPS_data['chart']['100026']
    newData['Suara_03'] = TPS_data['chart']['100027']
    newData['Dokumen'] = TPS_data['images']

    TPS_sus.append(newData)

    return 0
  
  for ID in TPS_done:
    TPS_val_req = requests.get('https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp' + kelurahan_ID + '/' 
                                + ID +'.json')
    TPS_val = TPS_val_req.json()
    TPS_val['ID'] = ID

    fault = []

    if TPS_val['administrasi'] == None:
    #   fault += ["Belum merekap data DPT tapi sudah merekap suara capres"]
    #   AppendTPSSus(ID, TPS_val, fault)
      continue
    #check total vote
    TVote = sum([i for i in TPS_val['chart'].values() if i])
    TAccepted = TPS_val['administrasi']['suara_sah']

    if TVote != TAccepted or TVote > 300:
      if TVote != TAccepted: fault += ["Suara total capres tidak sama dengan suara sah"] 
      if TVote > 300: fault += ["Suara total capres melebihi 300 suara"] 

      AppendTPSSus(ID, TPS_val, fault)
  return TPS_sus

provinceList = requests.get('https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/0.json')

province = st.selectbox("Pilih Provinsi",provinceList.json(), format_func= lambda x:x['nama'])

baseURL = 'https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp'

cityQuery = '/' + province['kode']
cityList = requests.get(baseURL + cityQuery + '.json')

city = st.selectbox("Pilih Kota", cityList.json(), format_func= lambda x:x['nama'])

kecamatanQuery = cityQuery + '/' + city['kode']
kecamatanList = requests.get(baseURL + kecamatanQuery + '.json')

kecamatan = st.selectbox("Pilih Kecamatan", kecamatanList.json(), format_func= lambda x:x['nama'])

kelurahanQuery = kecamatanQuery + '/' + kecamatan['kode']
kelurahanList = requests.get(baseURL + kelurahanQuery + '.json')

kelurahan = st.selectbox("Pilih Kelurahan", kelurahanList.json(), format_func= lambda x:x['nama'])

TPSQuery = kelurahanQuery + '/' + kelurahan['kode']

if st.button("Cek TPS",type="primary"):
  res = checkTPSSus(TPSQuery)
  if len(res) > 0:
    st.write(res)
  else:
    st.write("Belum ditemukan kecurangan di kelurahan ini")
    