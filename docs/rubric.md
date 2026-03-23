# USDA Egg Market Commentary Scoring Rubric

You are scoring the **National** commentary from the USDA Daily National Shell Egg Index Report. Your job is to convert qualitative market commentary into standardized numerical scores for a fixed set of dimensions.

You must score only what is explicitly stated in the National commentary text provided. Do not infer California conditions. Do not use outside knowledge. Do not guess missing values.

---

## Dimensions to Score

**Sentiment dimensions** (scored on individual ladders):

| # | Dimension | Scale |
|---|-----------|-------|
| 1 | PriceDirection | -3 to +3 |
| 2 | Undertone | -3 to +3 |
| 3 | RetailDemand | -3 to +3 |
| 4 | LooseDemand | -3 to +3 |
| 5 | FoodServiceDemand | -3 to +3 |
| 6 | Offerings | -3 to +3 (inverted) |
| 7 | Supplies | -3 to +3 (inverted) |
| 8 | MarketActivity | -2 to +2 |
| 9 | PriceConfidence | 0 to 100 |

**Computed values** (derived from abovee):

| Computed | Definition |
|----------|------------|
| SecondaryDemandScore | avg(LooseDemand, FoodServiceDemand) over available |
| SecondaryCoverage | 0.0 / 0.5 / 1.0 based on channel presence |
| NationalCoreIndex | Weighted composite, 0-100 scale |
| NationalExtendedIndex | Weighted composite incl. secondary demand, 0-100 scale |

---

## Critical Rules

1. **Score only explicit information.** If a dimension is not explicitly mentioned, return `null`.
2. **Missing does not mean neutral.** If loose egg demand or food service demand is not mentioned, use `null` -- not zero.
3. **Use canonical vocabulary mapping.** Map commentary language to the score ladders exactly as defined below.
4. **Combined-channel statements apply to each named channel.**
   - "Retail and food service demand is light to moderate" -> RetailDemand = -1, FoodServiceDemand = -1
   - "Demand into retail and loose egg channels is moderate" -> RetailDemand = 0, LooseDemand = 0
5. **Do not invent channels.** If a sentence says only "Demand is light to moderate" without naming loose egg or food service, do not assign those channel scores.
6. **Price confidence is separate from sentiment.** "Lightly tested," "not well tested," etc. affect PriceConfidence only.
7. **Renormalize indexes over observed dimensions only.** Exclude null dimensions and redistribute weights.
8. **Be conservative with ambiguous wording.** For mixed or size-split statements, calculate a weighted average and briefly explain.
9. **Output must be valid JSON** matching the schema defined in the output section.

---

## Score Ladders

### 1. PriceDirection

| Score | Vocabulary |
|------:|------------|
| -3.0 | sharply lower |
| -2.5 | lower to sharply lower |
| -2.0 | lower, mostly lower |
| -1.0 | steady to lower, about steady to lower, mixed leaning lower |
|  0.0 | steady, about steady, mostly steady, unchanged, mixed |
| +1.0 | steady to higher, steady to firm, steady to instances higher |
| +2.0 | higher, mostly higher |
| +3.0 | sharply higher, steady to sharply higher |

If no usable direction is given, return `null`.

### 2. Undertone

| Score | Vocabulary |
|------:|------------|
| -3.0 | lower |
| -2.5 | weak to lower |
| -2.0 | weak, generally weak |
| -1.0 | steady to weak, barely steady, mostly weak, steady to barely steady |
|  0.0 | steady, mostly steady, generally steady |
| +0.5 | fully steady |
| +1.0 | steady to firm, fully steady to firm |
| +2.0 | firm |
| +2.5 | firm to higher, steady to mostly higher |
| +3.0 | higher |

If a caution phrase is appended (e.g., "with some noting caution"), subtract 0.5.

### 3. Demand (RetailDemand, LooseDemand, FoodServiceDemand)

Same ladder for all three channels:

| Score | Vocabulary |
|------:|------------|
| -3.0 | very light |
| -2.0 | light |
| -1.0 | light to moderate |
|  0.0 | moderate, seasonally moderate, average, about moderate, mostly moderate |
| +0.5 | moderate to fairly good |
| +1.0 | fairly good, moderate to good |
| +2.0 | good |
| +3.0 | very good |

If a range is stated, score the midpoint (e.g., "light to moderate" = -1.0, "moderate to fairly good" = +0.5).

### 4. Offerings (inverted -- lighter = bullish)

| Score | Vocabulary |
|------:|------------|
| +3.0 | very light, held with confidence, confidently held |
| +2.0 | light |
| +1.0 | light to moderate, moderate to light |
|  0.0 | moderate, at least moderate |
| -1.0 | moderate to available, moderate to at times available |
| -2.0 | available |
| -3.0 | easily available, heavy |

### 5. Supplies (inverted -- tighter = bullish)

| Score | Vocabulary |
|------:|------------|
| +3.0 | short of full needs, very light, tightly balanced |
| +2.0 | light |
| +1.0 | moderate to light, light to moderate |
|  0.0 | moderate, mixed, varied |
| -1.0 | moderate to fully adequate, fully adequate to light |
| -2.0 | fully adequate, available |
| -3.0 | heavy, ample, easily available |

### 6. MarketActivity

| Score | Vocabulary |
|------:|------------|
| -2.0 | slow |
| -1.0 | slow to moderate, moderate to slow |
|  0.0 | moderate |
| +1.0 | moderate to active, moderate to instances active |
| +2.0 | active |

### 7. PriceConfidence (0-100 scale, not sentiment)

| Score | Vocabulary |
|------:|------------|
|    25 | untested, only one class tested |
|    40 | not well tested |
|    60 | very lightly tested, only lightly tested, light test, limited testing |
|    75 | lightly tested |
|   100 | no caution language about testing |

---

## Channel Assignment Rules

**RetailDemand** -- assign when commentary references:
- "retail demand," "retail movement," "movement into retail channels," "demand into retail channels"
- "cartoned demand" if clearly used as the main retail/carton channel

**LooseDemand** -- assign when commentary references:
- "loose egg demand," "loose egg movement," "loose egg channels," "loose demand"
- "cartoned and loose egg demand" if loose is explicitly named

**FoodServiceDemand** -- assign when commentary references:
- "food service demand," "food service movement," "demand into food service channels"

**Combined channel rule:** If a sentence names multiple channels together, assign the same score to each named channel.

---

## Handling Mixed or Split Statements

### Size-split pricing

If price direction differs by egg size, calculate a weighted average:
- Heavier/larger classes: weight = 2
- Medium/lighter classes: weight = 1

> Example: "higher for Large and Extra Large, lower for Medium"
> score = (2 + 2 - 2) / 3 = +0.67, round to nearest 0.5 -> **+0.5**

### Mixed sentence resolution

If wording mixes positive and negative descriptors within a single dimension, produce the best representative average and explain briefly.

> Example: "mixed, mostly steady on larger sizes and lower on Medium" -> approximately **-0.5**

---

## Index Calculation

### Step 1: SecondaryDemandScore

| Condition | Formula |
|-----------|---------|
| Both LooseDemand and FoodServiceDemand present | average(LooseDemand, FoodServiceDemand) |
| Only one present | that score |
| Neither present | `null` |

### Step 2: SecondaryCoverage

| Value | Meaning |
|------:|---------|
| 0.0 | Neither loose nor food service present |
| 0.5 | One of the two present |
| 1.0 | Both present |

### Step 3: NationalCoreIndex

Uses six core dimensions with these weights:

| Dimension | Weight |
|-----------|-------:|
| PriceDirection | 0.25 |
| Undertone | 0.30 |
| RetailDemand | 0.20 |
| Offerings | 0.10 |
| Supplies | 0.10 |
| MarketActivity | 0.05 |

```
NationalCoreIndexRaw = weighted average over observed core dimensions only
NationalCoreIndex = ((NationalCoreIndexRaw + 3) / 6) * 100
```

### Step 4: NationalExtendedIndex

Adds SecondaryDemandScore to the core dimensions:

| Dimension | Weight |
|-----------|-------:|
| PriceDirection | 0.22 |
| Undertone | 0.28 |
| RetailDemand | 0.18 |
| SecondaryDemandScore | 0.10 |
| Offerings | 0.10 |
| Supplies | 0.08 |
| MarketActivity | 0.04 |

```
NationalExtendedIndexRaw = weighted average over observed dimensions only
NationalExtendedIndex = ((NationalExtendedIndexRaw + 3) / 6) * 100
```

If SecondaryDemandScore is `null`, omit it and renormalize remaining weights.

### Step 5: FundamentalsCoreIndex

Isolates underlying market conditions by **excluding PriceDirection** from the
NationalCoreIndex and renormalizing the remaining five dimensions to sum to 1.0.
This shows whether demand, supply, and market tone are bullish or bearish
independent of the current price movement.

| Dimension | Weight |
|-----------|-------:|
| Undertone | 0.400 |
| RetailDemand | 0.267 |
| Offerings | 0.133 |
| Supplies | 0.133 |
| MarketActivity | 0.067 |

```
FundamentalsCoreIndexRaw = weighted average over observed dimensions only
FundamentalsCoreIndex = ((FundamentalsCoreIndexRaw + 3) / 6) * 100
```

Weights are derived from the NationalCoreIndex weights divided by
(1 − PriceDirection weight) = 0.75, then rounded to three decimal places.
