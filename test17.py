text = "中"

utf8_encoded = text.encode('utf-8')

print("UTF-8 編碼的字節資料:",utf8_encoded)

binary_representation = ' '.join(f'{byte:08b}' for byte in utf8_encoded)

print("UTF-8 編碼的二進制表示:",binary_representation)

for byte in utf8_encoded:
    print(byte)