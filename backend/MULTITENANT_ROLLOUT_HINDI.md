# Casino multi-tenant rollout

हर casino की identity `client_id` है और हर user की सुरक्षित identity `(client_id, user_id)` है। पुराने Gold365 records के लिए default client `demo` रखा गया है।

## 1. Backup

MongoDB backup लिए बिना migration apply न करें। पहले dry-run चलाएं:

```bash
cd ~/casino/backend
source venv/bin/activate
python scripts/migrate_multitenant.py
```

Output में `unresolved` zero होना चाहिए। उसके बाद:

```bash
python scripts/migrate_multitenant.py --apply
python scripts/migrate_multitenant.py
```

दूसरे dry-run में migratable/defaulted counts zero होने चाहिए।

## 2. Compatibility और strict mode

पहली deployment पर existing mobile app के लिए:

```env
ALLOW_LEGACY_GAME_IDENTITY=true
ALLOW_LEGACY_USER_ID=true
```

Updated mobile apps login response का `access_token` save करके हर private API पर `Authorization: Bearer TOKEN` भेजें। सभी branded apps update होने के बाद production में:

```env
ALLOW_LEGACY_GAME_IDENTITY=false
ALLOW_LEGACY_USER_ID=false
```

Strict mode में request body का `client_id` ignored होगा; token का client authoritative होगा।

## 3. Verification

```bash
python -m compileall -q .
python -m pytest -q
```

दो clients में same mobile बनाकर verify करें कि wallet और bets अलग रहें। Included test `test_same_username_is_isolated_between_clients` यही case check करता है।

## 4. Branded app contract

Login/create-account request में उस brand का client भेजें। Login response से `access_token` store करें। उसके बाद game, wallet, reports और notification calls में bearer token भेजें। User या app request में दूसरा client भेजे तब भी backend token वाले client को ही उपयोग करेगा।
