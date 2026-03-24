# SC4E, 2026

SC scripts taylored to Elettra 2.0

## Getting Started

```bash
git clone https://github.com/i-a-morozov/SC4E.git
mkdir -p elettra/data
python elettra/make/responces.py
python elettra/make/knobs.py
```

```bash
cd /home/morozov/SOFT/SimCom_petraIV/elettra

python scripts/000_generate.py \
  --config configuration.yaml \
  --data data \
  --machine elettra \
  --seed 1

python scripts/001_thread.py \
  --machine elettra \
  --get 00 \
  --set 01 \
  --seed 1 \
  --run-injection-correction \
  --run-last-corrector-wiggle
```
