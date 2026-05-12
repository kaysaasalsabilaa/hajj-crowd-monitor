def klasifikasi_keramaian(rerata_jumlah, rasio_lambat, X=60, Y=90, SH=0.5):
    """
    Menentukan label tingkat keramaian berdasarkan jumlah orang dan rasio lambat.

    Parameter:
        rerata_jumlah : rata-rata jumlah orang per window
        rasio_lambat  : proporsi pejalan kaki yang bergerak lambat (0.0–1.0)
        X             : ambang bawah keramaian sedang (default 60)
        Y             : ambang bawah keramaian tinggi (default 90)
        SH            : ambang rasio lambat (default 0.5)

    output:
        str - "TINGGI", "SEDANG", atau "RENDAH"
    """
    if rerata_jumlah >= Y:
        return "TINGGI"

    elif X <= rerata_jumlah < Y:
        if rasio_lambat >= SH:
            return "TINGGI"
        else:
            return "SEDANG"

    else:  # rerata_jumlah < X
        if rasio_lambat >= SH:
            return "SEDANG"
        else:
            return "RENDAH"


def klasifikasi_pergerakan(rasio_lambat, rerata_jumlah, X, SH=0.5):
    """
    Menentukan label kondisi pergerakan jamaah.

    Parameter:
        rasio_lambat  : proporsi pejalan kaki lambat (0.0–1.0)
        rerata_jumlah : rata-rata jumlah orang per window
        X             : ambang bawah keramaian (untuk filter kepadatan)
        SH            : ambang rasio lambat (default 0.5)

    Kembalikan:
        str — "TERSENDAT" atau "LANCAR"
    """
    if rerata_jumlah < X:
        return "LANCAR"
    return "TERSENDAT" if rasio_lambat >= SH else "LANCAR"