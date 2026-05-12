def classify_crowd(count_avg, slow_ratio, X=50, Y=100, SH=0.5):
    
    if count_avg >= Y:
        return "TINGGI"

    elif X <= count_avg < Y:
        if slow_ratio >= SH:
            return "TINGGI"
        else:
            return "SEDANG"

    else: 
        if slow_ratio >= SH:
            return "SEDANG"
        else:
            return "RENDAH"


def classify_movement(slow_ratio, count_avg, X, SH=0.5):
    
    if count_avg < X:
        return "LANCAR"  
    return "TERSENDAT" if slow_ratio >= SH else "LANCAR"