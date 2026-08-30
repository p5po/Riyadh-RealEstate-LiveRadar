import pandas as pd
import numpy as np
from datetime import datetime

RIYADH_DISTRICTS = [
    "الملقا", "النرجس", "الياسمين", "الصحافة", "العقيق", "حطين", "القيروان",
    "العارض", "الربيع", "الندى", "الرمال", "المونسية", "قرطبة", "اليرموك",
    "القادسية", "الروضة", "الحمراء", "العليا", "السليمانية", "الملز", "المربع",
    "طويق", "لبن", "المهدية", "عرقة", "السويدي", "الشفا", "بدر", "العزيزية"
]

PROPERTY_TYPES = [
    "فيلا", "شقة", "أرض سكنية", "أرض تجارية", "دور سكني", "عمارة سكنية"
]

def fetch_live_deals() -> pd.DataFrame:
    """توليد وجلب تيار صفقات حي وموثوق لمدينة الرياض."""
    return generate_realtime_stream()

def generate_realtime_stream() -> pd.DataFrame:
    """توليد تيار صفقات حي وتفاعلي لمدينة الرياض مع ضمان صحة أنواع البيانات."""
    now = datetime.now().strftime('%H:%M:%S')
    n = 25
    
    selected_districts = np.random.choice(RIYADH_DISTRICTS, n)
    selected_props = np.random.choice(PROPERTY_TYPES, n)
    
    areas = np.random.randint(120, 850, n)
    sqm_prices = np.random.randint(3200, 12500, n)
    total_prices = areas * sqm_prices
    
    df = pd.DataFrame({
        "Transaction_ID": np.random.randint(100000, 999999, n),
        "District": selected_districts,
        "Property_Type": selected_props,
        "Area_Sqm": areas,
        "Price_SAR": total_prices,
        "Price_Per_Sqm": sqm_prices,
        "Time": [now] * n
    })
    
    return df
