using Morpho as morpho;
using ERC20MockA as loanToken;
using ERC20MockB as collateralToken;
using IrmMock as irm;

methods {
    function Morpho.extSloads(bytes32[]) external returns bytes32[] => NONDET DELETE;
    function MorphoLib.collateral(address imorpho, Morpho.Id id, address user) internal returns (uint256) => morphoLibCollateral(id, user);
    function MorphoLib.lastUpdate(address imorpho, Morpho.Id id) internal returns (uint256) => morphoLibLastUpdate(id);
    function MorphoLib.fee(address imorpho, Morpho.Id id) internal returns (uint256) => morphoLibFee(id);
}

function morphoLibCollateral(Morpho.Id id, address user) returns uint256 {
    return morpho.position[id][user].collateral;
}

function morphoLibLastUpdate(Morpho.Id id) returns uint256 {
    return morpho.market[id].lastUpdate;
}

function morphoLibFee(Morpho.Id id) returns uint256 {
    return morpho.market[id].fee;
}

use builtin rule verifyFoundryFuzzTests;

override function init_fuzz_tests(method f, env e) {
    require e.msg.sender == currentContract;
    require 0 < e.block.timestamp && e.block.timestamp <= max_uint32; //, "morpho market stores timestamp in a uint128";
    require 0 < e.block.number && e.block.number <= max_uint32;

    reset_storage loanToken; // To avoid issues with totalSupply not being aligned with the balanceOf mapping
    reset_storage collateralToken; // To avoid issues with totalSupply not being aligned with the balanceOf mapping

    require currentContract.SUPPLIER != 0 && currentContract.SUPPLIER != morpho;
    require currentContract.BORROWER != 0 && currentContract.SUPPLIER != morpho;
    require currentContract.REPAYER != 0 && currentContract.SUPPLIER != morpho;
    require currentContract.ONBEHALF != 0 && currentContract.SUPPLIER != morpho;
    require currentContract.RECEIVER != 0 && currentContract.SUPPLIER != morpho;
    require currentContract.LIQUIDATOR != 0 && currentContract.SUPPLIER != morpho;
    require currentContract.OWNER != 0 && currentContract.SUPPLIER != morpho;
    require currentContract.FEE_RECIPIENT != 0 && currentContract.SUPPLIER != morpho;

    require morpho.owner == currentContract.OWNER;
    require forall address a. !morpho.isIrmEnabled[a];
    require forall uint256 u. !morpho.isLltvEnabled[u];
    require forall address a1. forall address a2. !morpho.isAuthorized[a1][a2];
    require forall Morpho.Id id. morpho.market[id].totalSupplyAssets == 0;
    require forall Morpho.Id id. morpho.market[id].totalSupplyShares == 0;
    require forall Morpho.Id id. morpho.market[id].totalBorrowAssets == 0;
    require forall Morpho.Id id. morpho.market[id].totalBorrowShares == 0;
    require forall Morpho.Id id. morpho.market[id].lastUpdate == 0;
    require forall Morpho.Id id. morpho.market[id].fee == 0;
    require forall Morpho.Id id. forall address a. morpho.position[id][a].supplyShares == 0;
    require forall Morpho.Id id. forall address a. morpho.position[id][a].borrowShares == 0;
    require forall Morpho.Id id. forall address a. morpho.position[id][a].collateral == 0;
    require forall address a. morpho.nonce[a] == 0;
    require morpho.feeRecipient != currentContract.FEE_RECIPIENT;

    env ownerEnv;
    require ownerEnv.msg.sender == currentContract.OWNER;
    morpho.enableIrm(ownerEnv, 0);
    morpho.enableIrm(ownerEnv, irm);
    morpho.enableLltv(ownerEnv, 0);
    morpho.setFeeRecipient(ownerEnv, currentContract.FEE_RECIPIENT);

    loanToken.approve(e, morpho, max_uint256);
    collateralToken.approve(e, morpho, max_uint256);

    env supplierEnv;
    require supplierEnv.msg.sender == currentContract.SUPPLIER;
    loanToken.approve(supplierEnv, morpho, max_uint256);
    collateralToken.approve(supplierEnv, morpho, max_uint256);

    env borrowerEnv;
    require borrowerEnv.msg.sender == currentContract.BORROWER;
    loanToken.approve(borrowerEnv, morpho, max_uint256);
    collateralToken.approve(borrowerEnv, morpho, max_uint256);

    env repayerEnv;
    require repayerEnv.msg.sender == currentContract.REPAYER;
    loanToken.approve(repayerEnv, morpho, max_uint256);
    collateralToken.approve(repayerEnv, morpho, max_uint256);

    env liquidatorEnv;
    require liquidatorEnv.msg.sender == currentContract.LIQUIDATOR;
    loanToken.approve(liquidatorEnv, morpho, max_uint256);
    collateralToken.approve(liquidatorEnv, morpho, max_uint256);

    env onbehalfEnv;
    require onbehalfEnv.msg.sender == currentContract.ONBEHALF;
    loanToken.approve(onbehalfEnv, morpho, max_uint256);
    collateralToken.approve(onbehalfEnv, morpho, max_uint256);
    morpho.setAuthorization(onbehalfEnv, currentContract.BORROWER, true);

    setLltv(e);
}
