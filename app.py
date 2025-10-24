import streamlit as st
import requests

# โหลดไฟล์ secrets จาก .txt
with open(".streamlit/secrets.txt", "r") as f:
    lines = f.readlines()
    secrets = {}
    for line in lines:
        key, value = line.strip().split("=", 1)
        secrets[key] = value
api_key = secrets["api.exchange_key"]

# (โค้ดส่วนที่เหลือเหมือนเดิม)
st.title("โปรแกรมคำนวณอัตราแลกเปลี่ยนเงินตรา")

# --- API Key (ใช้ secrets สำหรับ deploy) ---
api_key = st.secrets["api"]["exchange_key"]

# --- ส่วนเลือกสกุลเงินและจำนวนเงิน ---
st.subheader("ขั้นตอนที่ 1: ระบุรายละเอียดการแลกเปลี่ยน")

# รายการสกุลเงินยอดนิยม
currency_list = [
    'THB', 'USD', 'EUR', 'JPY', 'GBP', 'AUD', 
    'CAD', 'CHF', 'CNY', 'HKD', 'SGD', 'KRW'
]

col1, col2, col3 = st.columns(3)

with col1:
    amount = st.number_input("จำนวนเงิน:", min_value=1.0, value=100.0, step=1.0)
with col2:
    from_currency = st.selectbox("จากสกุลเงิน:", currency_list, index=1)  # default USD
with col3:
    to_currency = st.selectbox("เป็นสกุลเงิน:", currency_list, index=0)  # default THB

# --- ส่วนคำนวณและแสดงผล ---
if st.button("คำนวณอัตราแลกเปลี่ยน"):
    if not api_key:
        st.warning("กรุณาใส่ API Key ของคุณก่อนดำเนินการต่อ")
    elif from_currency == to_currency:
        st.warning("กรุณาเลือกสกุลเงินให้แตกต่างกัน")
    else:
        # สร้าง URL สำหรับเรียก API
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"
        
        try:
            # เรียก API และตรวจสอบ status code
            response = requests.get(url)
            if response.status_code != 200:
                st.error(f"เกิดข้อผิดพลาด: สถานะ {response.status_code} - เช็ค quota หรือ key")
            else:
                # Parse JSON
                data = response.json()
                
                # ตรวจสอบว่า API response สำเร็จหรือไม่
                if data.get("result") == "success":
                    # ดึงอัตราแลกเปลี่ยนของสกุลเงินปลายทาง
                    exchange_rate = data["conversion_rates"].get(to_currency)
                    
                    if exchange_rate:
                        # คำนวณผลลัพธ์
                        converted_amount = amount * exchange_rate
                        
                        # แสดงผลลัพธ์
                        st.success("ผลการแลกเปลี่ยน:")
                        st.metric(
                            label=f"{amount:,.2f} {from_currency}",
                            value=f"{converted_amount:,.2f} {to_currency}"
                        )
                        st.write(f"อัตราแลกเปลี่ยน: 1 {from_currency} = {exchange_rate:.4f} {to_currency}")
                        
                        # แสดงเวลา update
                        update_time = data.get("time_last_update_utc", "ไม่ทราบ")
                        st.caption(f"ข้อมูลอัปเดตล่าสุด: {update_time}")
                    else:
                        st.error(f"ไม่พบอัตราแลกเปลี่ยนสำหรับสกุลเงิน '{to_currency}'")
                else:
                    # กรณี API Key ไม่ถูกต้อง หรือมีข้อผิดพลาดอื่นๆ
                    error_type = data.get("error-type", "ไม่ทราบสาเหตุ")
                    st.error(f"เกิดข้อผิดพลาดจาก API: {error_type}")
        
        except requests.exceptions.JSONDecodeError:
            st.error("เกิดข้อผิดพลาด: ข้อมูลจาก API ไม่ใช่รูปแบบ JSON ที่ถูกต้อง")
        except requests.exceptions.RequestException as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ API: {e}")

st.info(f"อัปเดตข้อมูลล่าสุด: 24 ต.ค. 2568, 21:34 น. (เวลาประเทศไทย)")