import math

def potencjal_punktu(x_punkt, x_elektroda, rho1, rho2):
    granica = 50.0
    k12 = (rho2 - rho1) / (rho2 + rho1)
    
    odl = abs(x_punkt - x_elektroda)
    if odl == 0: 
        return 0.0

    x_obraz = 2 * granica - x_elektroda
    odl_obraz = abs(x_punkt - x_obraz)

    if x_elektroda <= granica:
        if x_punkt <= granica:
            return (rho1 / (2 * math.pi)) * (1 / odl + k12 / odl_obraz)
        else:
            return (rho1 / (2 * math.pi * odl)) * (1 + k12)
    else:
        if x_punkt > granica:
            return (rho2 / (2 * math.pi)) * (1 / odl - k12 / odl_obraz)
        else:
            return (rho2 / (2 * math.pi * odl)) * (1 - k12)


def oblicz(a, n, dx, rho1, rho2):
    x_max = 100
    prad = 1
    
    wsp_geom = math.pi * n * (n + 1) * a

    dlugosc_ukladu = (2 * n * a) + a

    x_pomiarowe = [round(dx * i, 2) for i in range(0, int((x_max - dlugosc_ukladu) / dx) + 1)]
    out = []
    
    for x_start in x_pomiarowe:
        xa = x_start
        xm = xa + (n * a)
        xn = xm + a
        xb = xn + (n * a)
        
        vma = potencjal_punktu(xm, xa, rho1, rho2)
        vmb = potencjal_punktu(xm, xb, rho1, rho2)
        vm = vma - vmb
              
        vna = potencjal_punktu(xn, xa, rho1, rho2)
        vnb = potencjal_punktu(xn, xb, rho1, rho2)
        vn = vna - vnb
              
        dv = vm - vn
        rhoa = wsp_geom * (dv / prad)
        
        srodek_ukladu = round((xa + xb) / 2, 2)
        out.append((srodek_ukladu, rhoa))
        
    return out