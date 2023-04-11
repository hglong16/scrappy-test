import requests

data = {
    "param": "FileTree",
    "oid": "54321-SpecificationVersion-18712961745-38dd1d5cbc90774e",
    "VALIDATION_TOKEN": "-8358238469492351389",
}
endpoint = "https://evergabe.sachsen.de/NetServer/DataProvider"

res = requests.post(endpoint, data=data, headers={
    'Cookie': 'JSESSIONID=m7jMpVGlnkRQ70WTQzqUjnoek3d2ChuPhCshiN66.1; privacy_modal={"cHJpdmFjeV9tb2RhbA==":true,"c25fY29udHJhc3Q=":true,"em9vbWVk":true,"ZmFjZWJvb2s=":false,"dHdpdHRlcg==":false,"aXNzdXU=":false,"eW91dHViZQ==":false,"SlNFU1NJT05JRA==":true}'
})

print(res.status_code)
print(res.content)
