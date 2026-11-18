-- Query 1
create view shippedVsCustDemand as
select
    cd.customer as customer,
    cd.item as item,
    coalesce(sum(so.qty), 0) as suppliedQty,
    cd.qty as demandQty
from customerDemand cd
left join shipOrders so
    on cd.customer = so.recipient and cd.item = so.item
group by cd.customer, cd.item, cd.qty
order by customer, item;

-- Query 2
create view totalManufItems as
select
    item as item,
    sum(qty) as totalManufQty
from manufOrders
group by item
order by item;

-- Query 3
create view matsUsedVsShipped as
select
    r.manuf as manuf,
    r.matItem as matItem,
    r.requiredQty as requiredQty,
    coalesce(s.shippedQty, 0) as shippedQty
from (
    select
        mo.manuf as manuf,
        bom.matItem as matItem,
        sum(mo.qty * bom.qtyMatPerItem) as requiredQty
    from manufOrders mo
    join billOfMaterials bom
        on mo.item = bom.prodItem
    group by mo.manuf, bom.matItem
) r
left join (
    select
        recipient as manuf,
        item as matItem,
        sum(qty) as shippedQty
    from shipOrders
    group by recipient, item
) s
    on r.manuf = s.manuf and r.matItem = s.matItem
order by manuf, matItem;

-- Query 4
create view producedVsShipped as
select
    mo.item as item,
    mo.manuf as manuf,
    coalesce(sum(so.qty), 0) as shippedOutQty,
    mo.qty as orderedQty
from manufOrders mo
left join shipOrders so
    on mo.item = so.item and mo.manuf = so.sender
group by mo.item, mo.manuf, mo.qty
order by item, manuf;

-- Query 5
create view suppliedVsShipped as
select
    so.item as item,
    so.supplier as supplier,
    so.qty as suppliedQty,
    coalesce(sum(shp.qty), 0) as shippedQty
from supplyOrders so
left join shipOrders shp
    on so.item = shp.item and so.supplier = shp.sender
group by so.item, so.supplier, so.qty
order by item, supplier;

-- Query 6
create view perSupplierCost as
select
    sd.supplier as supplier,
    case
        when coalesce(rc.rawCost, 0) <= sd.amt1
            then coalesce(rc.rawCost, 0)
        when coalesce(rc.rawCost, 0) <= sd.amt2
            then sd.amt1 + (coalesce(rc.rawCost, 0) - sd.amt1) * (1 - sd.disc1)
        else
            sd.amt1 + (sd.amt2 - sd.amt1) * (1 - sd.disc1) + (coalesce(rc.rawCost, 0) - sd.amt2) * (1 - sd.disc2)
    end as cost
from supplierDiscounts sd
left join (
    select
        so.supplier as supplier,
        sum(so.qty * sp.ppu) as rawCost
    from supplyOrders so
    join supplyUnitPricing sp
        on so.supplier = sp.supplier and so.item = sp.item
    group by so.supplier
) rc
    on sd.supplier = rc.supplier
order by supplier;

-- Query 7
create view perManufCost as
select
    md.manuf as manuf,
    case
        when coalesce(rc.rawCost, 0) <= md.amt1
            then coalesce(rc.rawCost, 0)
        else
            md.amt1 + (coalesce(rc.rawCost, 0) - md.amt1) * (1 - md.disc1)
    end as cost
from manufDiscounts md
left join (
    select
        mo.manuf as manuf,
        sum(mup.setUpCost + mo.qty * mup.prodCostPerUnit) as rawCost
    from manufOrders mo
    join manufUnitPricing mup
        on mo.manuf = mup.manuf and mo.item = mup.prodItem
    group by mo.manuf
) rc
    on md.manuf = rc.manuf
order by manuf;

-- Query 8
create view perShipperCost as
select
    shipper as shipper,
    sum(
        case
            when totalWeight is null or totalWeight = 0 then 0
            when discCost > minPackagePrice then discCost
            else minPackagePrice
        end
    ) as cost
from (
    select
        sp.shipper,
        sp.minPackagePrice,
        rw.totalWeight,
        case
            when (rw.totalWeight * sp.pricePerLb) <= sp.amt1
                then (rw.totalWeight * sp.pricePerLb)
            when (rw.totalWeight * sp.pricePerLb) <= sp.amt2
                then sp.amt1 + ((rw.totalWeight * sp.pricePerLb) - sp.amt1) * (1 - sp.disc1)
            else
                sp.amt1 + (sp.amt2 - sp.amt1) * (1 - sp.disc1) + ((rw.totalWeight * sp.pricePerLb) - sp.amt2) * (1 - sp.disc2)
        end as discCost
    from shippingPricing sp
    left join (
        select
            so.shipper as shipper,
            b_send.shipLoc as fromLoc,
            b_rec.shipLoc as toLoc,
            sum(so.qty * i.unitWeight) as totalWeight
        from shipOrders so
        join items i
            on so.item = i.item
        join busEntities b_send
            on so.sender = b_send.entity
        join busEntities b_rec
            on so.recipient = b_rec.entity
        group by so.shipper, b_send.shipLoc, b_rec.shipLoc
    ) rw
        on sp.shipper = rw.shipper
        and sp.fromLoc = rw.fromLoc
        and sp.toLoc = rw.toLoc
) routeCosts
group by shipper
order by shipper;

-- Query 9
create view totalCostBreakDown as
select
    s.supplyCost as supplyCost,
    m.manufCost as manufCost,
    sh.shippingCost as shippingCost,
    (s.supplyCost + m.manufCost + sh.shippingCost) as totalCost
from
    (select coalesce(sum(cost), 0) as supplyCost from perSupplierCost) s,
    (select coalesce(sum(cost), 0) as manufCost from perManufCost) m,
    (select coalesce(sum(cost), 0) as shippingCost from perShipperCost) sh;

-- Query 10
create view customersWithUnsatisfiedDemand as
select distinct customer
from shippedVsCustDemand
where suppliedQty < demandQty
order by customer;

-- Query 11
create view suppliersWithUnsentOrders as
select distinct supplier
from suppliedVsShipped
where shippedQty < suppliedQty
order by supplier;

-- Query 12
create view manufsWoutEnoughMats as
select distinct manuf
from matsUsedVsShipped
where shippedQty < requiredQty
order by manuf;

-- Query 13
create view manufsWithUnsentOrders as
select distinct manuf
from producedVsShipped
where shippedOutQty < orderedQty
order by manuf;

