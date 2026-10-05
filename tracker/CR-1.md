---
id: CR-1
type: change-request
title: "Personas koda pārbaude iesniegumā"
status: READY
priority: high
reporter: "Reģistrācijas nodaļa (izdomāts)"
owner: "@RB-art"
contract: "docs/openapi.yaml · POST /submissions · personalCode"
depends_on: []
exported: "2026-09-30 · Ezermalas pieteikumu sistēma (simulācija)"
data_check: "Nav personas datu, iekšējo adrešu vai pielikumu"
---

# CR-1 · Personas koda pārbaude iesniegumā

> Noteikumi vienkāršoti mācību vajadzībām.

## Apraksts (description)

Iesniegumos bieži ir nepareizi personas kodi. Sistēmai jāpārbauda, vai personas kods ir derīgs, un nederīgi iesniegumi jānoraida.

## Pieņemšanas kritēriji (acceptance criteria)

| # | Ievade (`personalCode`) | Sagaidāmais rezultāts |
|---|---|---|
| 1 | `32000000001` | 201, iesniegums saglabāts |
| 2 | `320000-00001` | 201, saglabāts bez defises (`32000000001`) |
| 3 | `" 32000000001 "` (atstarpes sākumā un beigās) | 201, atstarpes noņemtas (`32000000001`) |
| 4 | `3200000000` (10 cipari) | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT`, iesniegums netiek saglabāts |
| 5 | `320000000011` (12 cipari) | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT`, iesniegums netiek saglabāts |
| 6 | `32000000O01` (burts O cipara 0 vietā) | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT`, iesniegums netiek saglabāts |
| 7 | Lauka `personalCode` nav | 400 `VALIDATION_ERROR`, lauks `personalCode`, `REQUIRED`, iesniegums netiek saglabāts |
| 8 | `311299-21233` (vecā formāta sintētisks kods) | 201, iesniegums saglabāts |
| 9 | `3200-0000001` (defise nepareizā vietā) | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT`, iesniegums netiek saglabāts |
| 10 | `311299-21230` (vecais formāts, nepareizs kontrolcipars) | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_CHECKSUM`, iesniegums netiek saglabāts |
| 11 | `310299-12348` (vecais formāts, neeksistējošs datums 31.02.) | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_DATE`, iesniegums netiek saglabāts |

## Precizējumi (clarifications)

| Jautājums | Atbilde | Kas atbildēja, kad |
|---|---|---|
| Vai pieņemt kodu ar defisi? Kā to saglabāt? | Jā, ja defise ir pēc 6. cipara; saglabā bez defises | Produkta īpašnieks (pasniedzējs), S10, 2026-10-05 |
| Vai atstarpes koda sākumā/beigās noraidīt? | Nē, atstarpes noņem un kodu pieņem | Produkta īpašnieks (pasniedzējs), S10, 2026-10-05 |
| Kāds `issue` kods, ja lauka nav? | `REQUIRED`; visām formāta kļūdām `INVALID_FORMAT` | Produkta īpašnieks (pasniedzējs), S10, 2026-10-05 |
| Vai vecā formāta kodam pārbauda kontrolciparu un datumu? | Jā, abus. Nepareizs kontrolcipars: `INVALID_CHECKSUM`; neeksistējošs datums: `INVALID_DATE` | Produkta īpašnieks (pasniedzējs), 2026-10-05 |

## Ārpus apjoma (out of scope)

- Pārbaude, vai persona eksistē Iedzīvotāju reģistrā
- Ārvalstnieku identifikatori
- Jau saglabāto iesniegumu koda labošana

## Komentāri (comments)

- 2026-09-28 · Reģistrācijas nodaļa: "Vakar 12 iesniegumi ar nepareizu kodu. Visi jālabo ar roku."
