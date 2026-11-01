"""
Multi-Tenant Smart Contract & Blockchain Ledger engine for Zerovia Carbon Ledger.
Enforces Company Data Isolation, Shared Public Ledger Consensus,
1 Unit = 1 Ton CO2 conversion, and 400 PPM Safe Baseline Logic.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple

from core.config import (
    CHAIN_NAME,
    SMART_CONTRACT_ADDRESS,
    ORACLE_ADDRESS,
    DEFAULT_SAFE_PPM,
    DEFAULT_TOKEN_SYMBOL,
    TOKEN_NAME,
    CARBON_UNIT_TO_TONS,
    CLEAN_AIR_REWARD_RATE,
    PENALTY_BURN_RATE,
    OFFSET_PURCHASE_UNIT,
    OFFSET_UNIT_PRICE_USD,
    DEFAULT_TENANTS,
    MAX_HISTORY_POINTS,
    MAX_TRANSACTION_LOGS
)
from core.hardware import HardwareManager


@dataclass
class Transaction:
    tx_hash: str
    block_number: int
    timestamp: str
    tx_type: str       # MINT_REWARD | PENALTY_BURN | OFFSET_PURCHASE | RETIRE_CREDIT | AUDIT | ONBOARD_COMPANY
    from_address: str
    to_address: str
    amount: float      # In Z Credits (1 ZC = 1 Metric Ton CO2)
    tons_co2: float    # Explicit CO2 equivalent in Metric Tons
    ppm_recorded: Optional[float]
    status: str        # SUCCESS | PENALTY | FLAGGED
    notes: str
    company_id: str    # Tenant ownership for strict data isolation
    is_public: bool = True  # Verified on shared public blockchain ledger

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Block:
    index: int
    timestamp: str
    block_hash: str
    prev_hash: str
    validator: str
    transactions_count: int
    gas_used: str

    def to_dict(self) -> Dict:
        return asdict(self)


class CompanyTenant:
    """Represents an isolated company entity on the Zerovia Ledger."""

    def __init__(
        self,
        tenant_id: str,
        name: str,
        short_name: str,
        industry: str,
        device_id: str,
        vault_address: str,
        initial_balance: float = 350.0,
        baseline_ppm: float = 375.0,
        color: str = "#00F5A0",
        representative_name: str = "",
        access_key: str = "",
        status: str = "Active",
        created_at: str = ""
    ):
        self.id = tenant_id
        self.name = name
        self.short_name = short_name
        self.industry = industry
        self.device_id = device_id
        self.vault_address = vault_address
        self.representative_name = representative_name
        self.access_key = access_key
        self.status = status  # "Active", "Pending Approval", "Rejected"
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.initial_allocation = initial_balance
        self.token_balance: float = initial_balance   # In Z Credits (= Tons CO2)
        self.total_minted: float = initial_balance
        self.total_burned: float = 0.0
        self.total_offset_purchased: float = 0.0
        self.total_fines_count: int = 0
        self.baseline_ppm: float = baseline_ppm
        self.color: str = color
        
        # Isolated private state
        self.history: List[Dict] = []
        self.transactions: List[Transaction] = []
        self.hardware_mgr: HardwareManager = HardwareManager(baseline_ppm=baseline_ppm)
        self.consecutive_clean_cycles: int = 0
        self.consecutive_penalty_cycles: int = 0
        self.last_reading: Dict = {
            "ppm": baseline_ppm,
            "delta_ppm": 0.0,
            "temp": 24.5,
            "humidity": 51.0,
            "source": "Simulated Mock Stream",
            "timestamp": time.time()
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "industry": self.industry,
            "device_id": self.device_id,
            "vault_address": self.vault_address,
            "token_balance": round(self.token_balance, 2),
            "tons_co2_balance": round(self.token_balance * CARBON_UNIT_TO_TONS, 2),
            "total_minted": round(self.total_minted, 2),
            "total_burned": round(self.total_burned, 2),
            "total_offset_purchased": round(self.total_offset_purchased, 2),
            "total_fines_count": self.total_fines_count,
            "baseline_ppm": self.baseline_ppm,
            "color": self.color,
            "status": self.status,
            "representative_name": self.representative_name,
            "created_at": self.created_at
        }


class MultiTenantBlockchainLedger:
    """
    Manages the multi-tenant Zerovia blockchain:
    - Provides secure tenant data isolation (Company 1 vs Company 2).
    - Maintains a shared public blockchain ledger for cross-network consensus verification.
    - Evaluates safe threshold at 400 PPM (Micro-credit reward <= 400, Penalty burn > 400).
    - Enforces 1 Z Credit = 1 Ton CO2 tokenomics.
    - Dynamically onboards new companies.
    """

    def __init__(self):
        self.contract_address = SMART_CONTRACT_ADDRESS
        self.oracle_address = ORACLE_ADDRESS
        self.chain_name = CHAIN_NAME
        self.safe_ppm_threshold: float = DEFAULT_SAFE_PPM
        
        # Blockchain state
        self.total_blocks_mined: int = 2840
        self.last_block_hash: str = self._generate_hash("GENESIS_SEED_ZEROLUX_2026")
        self.public_blocks: List[Block] = []
        self.public_transactions: List[Transaction] = []

        # Tenants registry: tenant_id -> CompanyTenant
        self.tenants: Dict[str, CompanyTenant] = {}
        self._initialize_default_tenants()
        self._initialize_genesis_blocks()

    @staticmethod
    def _generate_hash(seed: str) -> str:
        """Create a realistic EVM transaction or block hash."""
        digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
        return f"0x{digest[:10]}...{digest[-6:]}"

    @staticmethod
    def _generate_full_hash(seed: str) -> str:
        return "0x" + hashlib.sha256(seed.encode('utf-8')).hexdigest()

    def _initialize_default_tenants(self):
        """Seed pre-configured demo companies."""
        for conf in DEFAULT_TENANTS:
            tenant = CompanyTenant(
                tenant_id=conf["id"],
                name=conf["name"],
                short_name=conf["short_name"],
                industry=conf["industry"],
                device_id=conf["device_id"],
                vault_address=conf["vault_address"],
                initial_balance=conf["initial_balance"],
                baseline_ppm=conf["baseline_ppm"],
                color=conf["color"]
            )
            self.tenants[tenant.id] = tenant

    def _initialize_genesis_blocks(self):
        """Seed the public blockchain ledger with initial genesis and onboarding transactions."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        genesis_block = Block(
            index=self.total_blocks_mined,
            timestamp=now_str,
            block_hash=self.last_block_hash,
            prev_hash="0x0000000000000000000000000000000000000000",
            validator="Zerovia-PoE-Validator-Quorum",
            transactions_count=len(self.tenants) + 1,
            gas_used="42,000 zkGas"
        )
        self.public_blocks.insert(0, genesis_block)

        # Genesis deployment transaction
        genesis_tx = Transaction(
            tx_hash=self._generate_hash("GENESIS_DEPLOY_2026"),
            block_number=self.total_blocks_mined,
            timestamp=now_str,
            tx_type="CONTRACT_DEPLOYED",
            from_address="0x0000000000000000000000000000000000000000",
            to_address=self.contract_address,
            amount=1000.0,
            tons_co2=1000.0,
            ppm_recorded=None,
            status="SUCCESS",
            notes="Smart Contract deployed: 1 Z Credit = 1 Ton CO2e tokenomics initialized.",
            company_id="system",
            is_public=True
        )
        self.public_transactions.insert(0, genesis_tx)

        # Initial onboarding transactions for seeded tenants
        for tenant in self.tenants.values():
            tx = Transaction(
                tx_hash=self._generate_hash(f"ONBOARD_{tenant.id}"),
                block_number=self.total_blocks_mined,
                timestamp=now_str,
                tx_type="ONBOARD_COMPANY",
                from_address=self.contract_address,
                to_address=tenant.vault_address,
                amount=tenant.token_balance,
                tons_co2=tenant.token_balance * CARBON_UNIT_TO_TONS,
                ppm_recorded=tenant.baseline_ppm,
                status="SUCCESS",
                notes=f"Tenant '{tenant.name}' registered. Initial vault: {tenant.token_balance:.1f} ZC ({tenant.token_balance:.1f} Tons CO2).",
                company_id=tenant.id,
                is_public=True
            )
            tenant.transactions.insert(0, tx)
            self.public_transactions.insert(0, tx)

    def onboard_new_company(
        self,
        name: str,
        short_name: str,
        industry: str,
        device_id: str,
        initial_balance: float = 300.0,
        baseline_ppm: float = 380.0,
        representative_name: str = "",
        access_key: str = ""
    ) -> CompanyTenant:
        """Dynamically onboard a new company profile during runtime demonstrations."""
        clean_name = name.strip()
        tenant_id = f"comp_{hashlib.md5(clean_name.encode()).hexdigest()[:6]}"
        
        # Generate random unique EVM vault address
        vault_hash = hashlib.sha256(f"VAULT_{tenant_id}_{time.time()}".encode()).hexdigest()
        vault_address = f"0x{vault_hash[:8]}...{vault_hash[-6:]}"
        
        colors = ["#A855F7", "#EC4899", "#3B82F6", "#F59E0B", "#10B981"]
        assigned_color = colors[len(self.tenants) % len(colors)]

        tenant = CompanyTenant(
            tenant_id=tenant_id,
            name=clean_name,
            short_name=short_name.strip() or clean_name[:12],
            industry=industry.strip() or "Sustainable Operations",
            device_id=device_id.strip() or f"ESP32-GAS-NODE-{len(self.tenants)+1:02d}",
            vault_address=vault_address,
            initial_balance=initial_balance,
            baseline_ppm=baseline_ppm,
            color=assigned_color,
            representative_name=representative_name.strip(),
            access_key=access_key.strip()
        )
        self.tenants[tenant_id] = tenant

        # Record public and private onboarding block transaction
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_blocks_mined += 1
        tx_hash = self._generate_hash(f"ONBOARD_NEW_{tenant_id}_{time.time()}")
        self.last_block_hash = self._generate_hash(f"BLOCK_{self.total_blocks_mined}")

        tx = Transaction(
            tx_hash=tx_hash,
            block_number=self.total_blocks_mined,
            timestamp=now_str,
            tx_type="ONBOARD_COMPANY",
            from_address=self.contract_address,
            to_address=tenant.vault_address,
            amount=initial_balance,
            tons_co2=initial_balance * CARBON_UNIT_TO_TONS,
            ppm_recorded=baseline_ppm,
            status="SUCCESS",
            notes=f"New Tenant Onboarded: '{tenant.name}' assigned vault {vault_address} with {initial_balance:.1f} ZC ({initial_balance:.1f} Tons CO2).",
            company_id=tenant.id,
            is_public=True
        )
        tenant.transactions.insert(0, tx)
        self.public_transactions.insert(0, tx)
        return tenant

    def register_pending_customer(
        self,
        name: str,
        short_name: str,
        industry: str,
        device_id: str,
        initial_balance: float = 300.0,
        baseline_ppm: float = 380.0,
        representative_name: str = "",
        access_key: str = ""
    ) -> CompanyTenant:
        """Register a customer applicant with status 'Pending Approval' for Director review."""
        clean_name = name.strip()
        tenant_id = f"comp_{hashlib.md5(clean_name.encode()).hexdigest()[:6]}"

        vault_hash = hashlib.sha256(f"VAULT_{tenant_id}_{time.time()}".encode()).hexdigest()
        vault_address = f"0x{vault_hash[:8]}...{vault_hash[-6:]}"

        colors = ["#A855F7", "#EC4899", "#3B82F6", "#F59E0B", "#10B981"]
        assigned_color = colors[len(self.tenants) % len(colors)]

        tenant = CompanyTenant(
            tenant_id=tenant_id,
            name=clean_name,
            short_name=short_name.strip() or clean_name[:12],
            industry=industry.strip() or "Sustainable Operations",
            device_id=device_id.strip() or f"ESP32-GAS-NODE-{len(self.tenants)+1:02d}",
            vault_address=vault_address,
            initial_balance=initial_balance,
            baseline_ppm=baseline_ppm,
            color=assigned_color,
            representative_name=representative_name.strip(),
            access_key=access_key.strip(),
            status="Pending Approval"
        )
        self.tenants[tenant_id] = tenant
        return tenant

    def approve_tenant(self, tenant_id: str) -> Optional[CompanyTenant]:
        """Director approves a pending company profile, activating vault & mining consensus block."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None

        tenant.status = "Active"

        # Record public and private onboarding block transaction upon Director approval
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_blocks_mined += 1
        tx_hash = self._generate_hash(f"APPROVAL_{tenant_id}_{time.time()}")
        self.last_block_hash = self._generate_hash(f"BLOCK_{self.total_blocks_mined}")

        tx = Transaction(
            tx_hash=tx_hash,
            block_number=self.total_blocks_mined,
            timestamp=now_str,
            tx_type="DIRECTOR_APPROVED_TENANT",
            from_address=self.contract_address,
            to_address=tenant.vault_address,
            amount=tenant.token_balance,
            tons_co2=tenant.token_balance * CARBON_UNIT_TO_TONS,
            ppm_recorded=tenant.baseline_ppm,
            status="SUCCESS",
            notes=f"Director Approved: '{tenant.name}' registered to active registry with vault {tenant.vault_address} ({tenant.token_balance:.1f} ZC = {tenant.token_balance:.1f} Tons CO2).",
            company_id=tenant.id,
            is_public=True
        )
        tenant.transactions.insert(0, tx)
        self.public_transactions.insert(0, tx)
        return tenant

    def reject_tenant(self, tenant_id: str) -> bool:
        """Director rejects a pending company profile."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        tenant.status = "Rejected"
        return True

    def get_active_tenants(self) -> Dict[str, CompanyTenant]:
        """Returns all dynamically approved, active enterprise companies."""
        return {tid: t for tid, t in self.tenants.items() if t.status == "Active"}

    def get_pending_tenants(self) -> Dict[str, CompanyTenant]:
        """Returns all applicants waiting in the Director Approval Queue."""
        return {tid: t for tid, t in self.tenants.items() if t.status == "Pending Approval"}

    def determine_compliance_status(self, ppm: float) -> Tuple[str, str, str]:
        """
        Calculates compliance status based on the 400 PPM Safe Baseline:
        - <= 400 PPM: Green (Safe baseline met, clean air micro-credits rewarded)
        - > 400 PPM: Fine Enforced (Threshold breached, automated penalty burned)
        """
        if ppm <= self.safe_ppm_threshold:
            return (
                "Green",
                "#00F5A0",
                f"Safe air quality (<= {self.safe_ppm_threshold:.0f} PPM). Micro-credit incentive active."
            )
        else:
            return (
                "Fine Enforced",
                "#EF4444",
                f"Emission breach (> {self.safe_ppm_threshold:.0f} PPM). Automated penalty burned."
            )

    def process_tenant_reading(self, tenant_id: str, ppm: float, sensor_source: str) -> Dict:
        """
        Processes a sensor reading for a specific isolated company tenant.
        Applies smart contract logic:
        - <= 400 PPM: Rewards clean air micro-credits (+0.25 ZC = +0.25 Tons CO2).
        - > 400 PPM: Burns penalty credits (-0.50 ZC = -0.50 Tons CO2).
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {}

        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        status, color, desc = self.determine_compliance_status(ppm)
        tx_triggered = None

        if status == "Green":
            tenant.consecutive_clean_cycles += 1
            tenant.consecutive_penalty_cycles = 0

            # Reward clean air micro-credit every clean cycle
            reward_zc = CLEAN_AIR_REWARD_RATE
            reward_tons = reward_zc * CARBON_UNIT_TO_TONS
            tenant.token_balance += reward_zc
            tenant.total_minted += reward_zc

            self.total_blocks_mined += 1
            seed = f"MINT_{tenant.id}_{self.total_blocks_mined}_{time.time()}_{ppm}"
            tx_hash = self._generate_hash(seed)
            self.last_block_hash = self._generate_hash(f"BLOCK_{self.total_blocks_mined}_{seed}")

            tx_triggered = Transaction(
                tx_hash=tx_hash,
                block_number=self.total_blocks_mined,
                timestamp=now_str,
                tx_type="MINT_REWARD",
                from_address=self.contract_address,
                to_address=tenant.vault_address,
                amount=reward_zc,
                tons_co2=reward_tons,
                ppm_recorded=ppm,
                status="SUCCESS",
                notes=f"Air quality safe ({ppm:.1f} PPM <= 400). Rewarded +{reward_zc:.2f} ZC (+{reward_tons:.2f} Tons CO2 avoided).",
                company_id=tenant.id,
                is_public=True
            )
            tenant.transactions.insert(0, tx_triggered)
            self.public_transactions.insert(0, tx_triggered)

        else: # Fine Enforced (> 400 PPM)
            tenant.consecutive_penalty_cycles += 1
            tenant.consecutive_clean_cycles = 0

            penalty_zc = PENALTY_BURN_RATE
            penalty_tons = penalty_zc * CARBON_UNIT_TO_TONS
            tenant.token_balance = max(0.0, tenant.token_balance - penalty_zc)
            tenant.total_burned += penalty_zc
            tenant.total_fines_count += 1

            self.total_blocks_mined += 1
            seed = f"BURN_{tenant.id}_{self.total_blocks_mined}_{time.time()}_{ppm}"
            tx_hash = self._generate_hash(seed)
            self.last_block_hash = self._generate_hash(f"BLOCK_{self.total_blocks_mined}_{seed}")

            tx_triggered = Transaction(
                tx_hash=tx_hash,
                block_number=self.total_blocks_mined,
                timestamp=now_str,
                tx_type="PENALTY_BURN",
                from_address=tenant.vault_address,
                to_address="0x000000000000000000000000000000000000dEaD",
                amount=-penalty_zc,
                tons_co2=-penalty_tons,
                ppm_recorded=ppm,
                status="PENALTY",
                notes=f"Emission breach ({ppm:.1f} PPM > 400). Automated fine: -{penalty_zc:.2f} ZC (-{penalty_tons:.2f} Tons CO2 penalized).",
                company_id=tenant.id,
                is_public=True
            )
            tenant.transactions.insert(0, tx_triggered)
            self.public_transactions.insert(0, tx_triggered)

        # Cap memory logs
        if len(tenant.transactions) > MAX_TRANSACTION_LOGS:
            tenant.transactions = tenant.transactions[:MAX_TRANSACTION_LOGS]
        if len(self.public_transactions) > MAX_TRANSACTION_LOGS * 2:
            self.public_transactions = self.public_transactions[:MAX_TRANSACTION_LOGS * 2]

        # Record company private history
        history_entry = {
            "timestamp": now.strftime("%H:%M:%S"),
            "datetime": now_str,
            "ppm": ppm,
            "status": status,
            "color": color,
            "balance": round(tenant.token_balance, 2),
            "tons_co2": round(tenant.token_balance * CARBON_UNIT_TO_TONS, 2),
            "source": sensor_source
        }
        tenant.history.append(history_entry)
        if len(tenant.history) > MAX_HISTORY_POINTS:
            tenant.history = tenant.history[-MAX_HISTORY_POINTS:]

        return {
            "status": status,
            "color": color,
            "desc": desc,
            "token_balance": round(tenant.token_balance, 2),
            "tons_co2": round(tenant.token_balance * CARBON_UNIT_TO_TONS, 2),
            "tx_triggered": tx_triggered.to_dict() if tx_triggered else None
        }

    def purchase_offset_for_tenant(self, tenant_id: str, amount_zc: float = OFFSET_PURCHASE_UNIT) -> Optional[Transaction]:
        """User purchases voluntary carbon offsets (1 ZC = 1 Ton CO2 offset)."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tons_offset = amount_zc * CARBON_UNIT_TO_TONS
        tenant.token_balance += amount_zc
        tenant.total_offset_purchased += amount_zc
        self.total_blocks_mined += 1

        seed = f"PURCHASE_{tenant.id}_{time.time()}_{amount_zc}"
        tx_hash = self._generate_hash(seed)
        self.last_block_hash = self._generate_hash(f"BLOCK_{self.total_blocks_mined}_{seed}")

        tx = Transaction(
            tx_hash=tx_hash,
            block_number=self.total_blocks_mined,
            timestamp=now_str,
            tx_type="OFFSET_PURCHASE",
            from_address="0xCarbonOffsetPool...981c",
            to_address=tenant.vault_address,
            amount=amount_zc,
            tons_co2=tons_offset,
            ppm_recorded=None,
            status="SUCCESS",
            notes=f"Purchased +{amount_zc:.1f} Z Credits (+{tons_offset:.1f} Tons CO2 Offset) via zkEVM on-ramp.",
            company_id=tenant.id,
            is_public=True
        )
        tenant.transactions.insert(0, tx)
        self.public_transactions.insert(0, tx)
        return tx

    def retire_credits_for_tenant(self, tenant_id: str, amount_zc: float) -> Optional[Transaction]:
        """Permanently burns Z Credits for ESG certification (1 ZC = 1 Ton CO2 retired)."""
        tenant = self.tenants.get(tenant_id)
        if not tenant or amount_zc > tenant.token_balance or amount_zc <= 0:
            return None

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tons_retired = amount_zc * CARBON_UNIT_TO_TONS
        tenant.token_balance -= amount_zc
        tenant.total_burned += amount_zc
        self.total_blocks_mined += 1

        seed = f"RETIRE_{tenant.id}_{time.time()}_{amount_zc}"
        tx_hash = self._generate_hash(seed)

        tx = Transaction(
            tx_hash=tx_hash,
            block_number=self.total_blocks_mined,
            timestamp=now_str,
            tx_type="RETIRE_CREDIT",
            from_address=tenant.vault_address,
            to_address="0x000000000000000000000000000000000000dEaD",
            amount=-amount_zc,
            tons_co2=-tons_retired,
            ppm_recorded=None,
            status="SUCCESS",
            notes=f"Permanently retired {amount_zc:.1f} Z Credits ({tons_retired:.1f} Tons CO2e) for official ESG compliance.",
            company_id=tenant.id,
            is_public=True
        )
        tenant.transactions.insert(0, tx)
        self.public_transactions.insert(0, tx)
        return tx

    def trigger_audit(self, tenant_id: Optional[str] = None) -> Transaction:
        """Triggers an on-chain smart contract compliance audit."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_blocks_mined += 1
        seed = f"AUDIT_{tenant_id or 'GLOBAL'}_{time.time()}"
        tx_hash = self._generate_hash(seed)

        tenant_name = self.tenants[tenant_id].name if tenant_id and tenant_id in self.tenants else "All Multi-Tenant Quorum"
        target_vault = self.tenants[tenant_id].vault_address if tenant_id and tenant_id in self.tenants else self.contract_address

        tx = Transaction(
            tx_hash=tx_hash,
            block_number=self.total_blocks_mined,
            timestamp=now_str,
            tx_type="AUDIT",
            from_address=self.oracle_address,
            to_address=target_vault,
            amount=0.0,
            tons_co2=0.0,
            ppm_recorded=None,
            status="SUCCESS",
            notes=f"Oracle Consensus Verification for '{tenant_name}'. All state merkle roots verified.",
            company_id=tenant_id or "system",
            is_public=True
        )
        if tenant_id and tenant_id in self.tenants:
            self.tenants[tenant_id].transactions.insert(0, tx)
        self.public_transactions.insert(0, tx)
        return tx

    def get_public_ledger_transactions(self) -> List[Transaction]:
        """Returns the shared public blockchain ledger visible to all participants."""
        return self.public_transactions

    def get_tenant_transactions(self, tenant_id: str) -> List[Transaction]:
        """Returns isolated private transactions for a specific tenant."""
        tenant = self.tenants.get(tenant_id)
        return tenant.transactions if tenant else []

    def get_aggregated_stats(self) -> Dict:
        """Computes global network metrics across all active approved tenants for Issuer Admin view."""
        active_tenants = self.get_active_tenants()
        total_balance = sum(t.token_balance for t in active_tenants.values())
        total_minted = sum(t.total_minted for t in active_tenants.values())
        total_burned = sum(t.total_burned for t in active_tenants.values())
        total_offset = sum(t.total_offset_purchased for t in active_tenants.values())
        total_fines = sum(t.total_fines_count for t in active_tenants.values())
        
        return {
            "total_companies": len(active_tenants),
            "pending_count": len(self.get_pending_tenants()),
            "total_balance_zc": round(total_balance, 2),
            "total_tons_co2": round(total_balance * CARBON_UNIT_TO_TONS, 2),
            "total_minted_zc": round(total_minted, 2),
            "total_burned_zc": round(total_burned, 2),
            "total_offset_zc": round(total_offset, 2),
            "total_fines": total_fines,
            "blocks_mined": self.total_blocks_mined
        }


# Global shared singleton instance for cross-session two-way synchronization
_SHARED_LEDGER_INSTANCE: Optional[MultiTenantBlockchainLedger] = None

def get_shared_ledger() -> MultiTenantBlockchainLedger:
    """Returns the process-level singleton instance ensuring synchronized state across tabs/sessions."""
    global _SHARED_LEDGER_INSTANCE
    if _SHARED_LEDGER_INSTANCE is None:
        _SHARED_LEDGER_INSTANCE = MultiTenantBlockchainLedger()
    return _SHARED_LEDGER_INSTANCE
