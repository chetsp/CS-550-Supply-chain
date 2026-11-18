-- ============================================================================
-- CS 550 / CS 450: Database Management Project Assignment - Part 1
-- Database Design: DDL Specification with Integrity & CHECK Constraints
-- ============================================================================
-- Note: As instructed in Part 1, this design models the conceptual supply chain
-- domain with full relational normalization and integrity constraints, rather
-- than reverse-engineering the simplified query-testing tables of Part 2.
-- ============================================================================

-- Drop tables in reverse dependency order if they already exist
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE ShippingOrders CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE ManufacturingOrders CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE SupplyOrders CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE CustomerDemand CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE ShippingPricing CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE ManufacturingPricing CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE SupplyPricing CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE BillOfMaterials CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE Shippers CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE Customers CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE Manufacturers CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE Suppliers CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE BusinessEntities CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE ProductItems CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE MaterialItems CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE Items CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- ============================================================================
-- 1. BASE ENTITIES & SPECIALIZATION HIERARCHIES
-- ============================================================================

-- Superclass: Items
-- Captures all items in the supply chain (both raw materials and finished products).
CREATE TABLE Items (
    itemId          VARCHAR2(30)    NOT NULL,
    itemName        VARCHAR2(100)   NOT NULL,
    unitWeight      NUMBER(10, 2)   NOT NULL,
    itemCategory    VARCHAR2(20)    NOT NULL,
    CONSTRAINT PK_Items PRIMARY KEY (itemId),
    CONSTRAINT CHK_Items_Weight CHECK (unitWeight > 0),
    CONSTRAINT CHK_Items_Category CHECK (itemCategory IN ('MATERIAL', 'PRODUCT', 'BOTH'))
);

-- Subclass: MaterialItems
-- Items that serve as raw materials or component parts in production.
CREATE TABLE MaterialItems (
    itemId          VARCHAR2(30)    NOT NULL,
    materialType    VARCHAR2(50),
    CONSTRAINT PK_MaterialItems PRIMARY KEY (itemId),
    CONSTRAINT FK_MaterialItems_Items FOREIGN KEY (itemId)
        REFERENCES Items(itemId) ON DELETE CASCADE
);

-- Subclass: ProductItems
-- Finished product items manufactured from components.
CREATE TABLE ProductItems (
    itemId          VARCHAR2(30)    NOT NULL,
    productLine     VARCHAR2(50),
    CONSTRAINT PK_ProductItems PRIMARY KEY (itemId),
    CONSTRAINT FK_ProductItems_Items FOREIGN KEY (itemId)
        REFERENCES Items(itemId) ON DELETE CASCADE
);

-- Superclass: BusinessEntities
-- All business participants: suppliers, manufacturers, shippers, customers.
CREATE TABLE BusinessEntities (
    entityId        VARCHAR2(30)    NOT NULL,
    name            VARCHAR2(100)   NOT NULL,
    shipLoc         VARCHAR2(50)    NOT NULL,  -- Shipping location identifier/city
    address         VARCHAR2(150)   NOT NULL,
    phone           VARCHAR2(20)    NOT NULL,
    web             VARCHAR2(100),
    contactInfo     VARCHAR2(100)   NOT NULL,
    CONSTRAINT PK_BusinessEntities PRIMARY KEY (entityId),
    CONSTRAINT CHK_BE_Phone CHECK (LENGTH(TRIM(phone)) >= 7)
);

-- Subclass: Suppliers
-- Supplies raw materials / items with optional volume discount policies.
CREATE TABLE Suppliers (
    supplierId          VARCHAR2(30)    NOT NULL,
    discountThreshold1  NUMBER(12, 2)   DEFAULT 0.00 NOT NULL,
    discountPercent1    NUMBER(5, 4)    DEFAULT 0.0000 NOT NULL, -- e.g., 0.10 for 10%
    discountThreshold2  NUMBER(12, 2)   DEFAULT 0.00 NOT NULL,
    discountPercent2    NUMBER(5, 4)    DEFAULT 0.0000 NOT NULL,
    CONSTRAINT PK_Suppliers PRIMARY KEY (supplierId),
    CONSTRAINT FK_Suppliers_BE FOREIGN KEY (supplierId)
        REFERENCES BusinessEntities(entityId) ON DELETE CASCADE,
    CONSTRAINT CHK_Sup_Disc1 CHECK (discountPercent1 >= 0.0000 AND discountPercent1 <= 1.0000),
    CONSTRAINT CHK_Sup_Disc2 CHECK (discountPercent2 >= 0.0000 AND discountPercent2 <= 1.0000),
    CONSTRAINT CHK_Sup_Thresholds CHECK (discountThreshold1 >= 0 AND discountThreshold2 >= discountThreshold1),
    CONSTRAINT CHK_Sup_DiscRate CHECK (discountPercent2 >= discountPercent1)
);

-- Subclass: Manufacturers
-- Produces product items with production discounts on base cost exceeding a threshold.
CREATE TABLE Manufacturers (
    manufId             VARCHAR2(30)    NOT NULL,
    discountThreshold   NUMBER(12, 2)   DEFAULT 0.00 NOT NULL,
    discountPercent     NUMBER(5, 4)    DEFAULT 0.0000 NOT NULL,
    CONSTRAINT PK_Manufacturers PRIMARY KEY (manufId),
    CONSTRAINT FK_Manufacturers_BE FOREIGN KEY (manufId)
        REFERENCES BusinessEntities(entityId) ON DELETE CASCADE,
    CONSTRAINT CHK_Manuf_DiscPercent CHECK (discountPercent >= 0.0000 AND discountPercent <= 1.0000),
    CONSTRAINT CHK_Manuf_DiscThreshold CHECK (discountThreshold >= 0)
);

-- Subclass: Customers
-- Entities demanding products or items.
CREATE TABLE Customers (
    customerId          VARCHAR2(30)    NOT NULL,
    customerType        VARCHAR2(30)    DEFAULT 'STANDARD' NOT NULL,
    creditLimit         NUMBER(12, 2)   DEFAULT 10000.00 NOT NULL,
    CONSTRAINT PK_Customers PRIMARY KEY (customerId),
    CONSTRAINT FK_Customers_BE FOREIGN KEY (customerId)
        REFERENCES BusinessEntities(entityId) ON DELETE CASCADE,
    CONSTRAINT CHK_Cust_CreditLimit CHECK (creditLimit >= 0)
);

-- Subclass: Shippers
-- Logistics providers moving goods between locations.
CREATE TABLE Shippers (
    shipperId           VARCHAR2(30)    NOT NULL,
    trackingUrl         VARCHAR2(150),
    CONSTRAINT PK_Shippers PRIMARY KEY (shipperId),
    CONSTRAINT FK_Shippers_BE FOREIGN KEY (shipperId)
        REFERENCES BusinessEntities(entityId) ON DELETE CASCADE
);

-- ============================================================================
-- 2. BILL OF MATERIALS (BOM) RELATIONSHIP
-- ============================================================================

-- A product item is composed of material items in specific quantities.
CREATE TABLE BillOfMaterials (
    prodItemId          VARCHAR2(30)    NOT NULL,
    matItemId           VARCHAR2(30)    NOT NULL,
    qtyMatPerItem       NUMBER(10)      NOT NULL,
    CONSTRAINT PK_BillOfMaterials PRIMARY KEY (prodItemId, matItemId),
    CONSTRAINT FK_BOM_Product FOREIGN KEY (prodItemId)
        REFERENCES ProductItems(itemId) ON DELETE CASCADE,
    CONSTRAINT FK_BOM_Material FOREIGN KEY (matItemId)
        REFERENCES MaterialItems(itemId) ON DELETE CASCADE,
    CONSTRAINT CHK_BOM_Qty CHECK (qtyMatPerItem > 0),
    -- Prevent an item from being composed directly of itself
    CONSTRAINT CHK_BOM_NoSelfLoop CHECK (prodItemId <> matItemId)
);

-- ============================================================================
-- 3. PRICING RELATIONSHIPS / WEAK ENTITIES
-- ============================================================================

-- Supply Unit Pricing: Price per unit charged by a supplier for a supplied item.
CREATE TABLE SupplyPricing (
    supplierId          VARCHAR2(30)    NOT NULL,
    itemId              VARCHAR2(30)    NOT NULL,
    pricePerUnit        NUMBER(10, 2)   NOT NULL,
    CONSTRAINT PK_SupplyPricing PRIMARY KEY (supplierId, itemId),
    CONSTRAINT FK_SupplyPricing_Supplier FOREIGN KEY (supplierId)
        REFERENCES Suppliers(supplierId) ON DELETE CASCADE,
    CONSTRAINT FK_SupplyPricing_Item FOREIGN KEY (itemId)
        REFERENCES Items(itemId) ON DELETE CASCADE,
    CONSTRAINT CHK_Supply_PPU CHECK (pricePerUnit > 0)
);

-- Manufacturing Unit Pricing: Set up cost and unit cost for producing a product.
CREATE TABLE ManufacturingPricing (
    manufId             VARCHAR2(30)    NOT NULL,
    prodItemId          VARCHAR2(30)    NOT NULL,
    setUpCost           NUMBER(10, 2)   DEFAULT 0.00 NOT NULL,
    prodCostPerUnit     NUMBER(10, 2)   NOT NULL,
    CONSTRAINT PK_ManufPricing PRIMARY KEY (manufId, prodItemId),
    CONSTRAINT FK_ManufPricing_Manuf FOREIGN KEY (manufId)
        REFERENCES Manufacturers(manufId) ON DELETE CASCADE,
    CONSTRAINT FK_ManufPricing_Product FOREIGN KEY (prodItemId)
        REFERENCES ProductItems(itemId) ON DELETE CASCADE,
    CONSTRAINT CHK_Manuf_SetUpCost CHECK (setUpCost >= 0),
    CONSTRAINT CHK_Manuf_ProdCost CHECK (prodCostPerUnit > 0)
);

-- Shipping Route Pricing: Per-route pricing charged by shippers based on weight.
CREATE TABLE ShippingPricing (
    shipperId           VARCHAR2(30)    NOT NULL,
    fromLoc             VARCHAR2(50)    NOT NULL,
    toLoc               VARCHAR2(50)    NOT NULL,
    minPackagePrice     NUMBER(10, 2)   DEFAULT 0.00 NOT NULL,
    pricePerLb          NUMBER(10, 2)   NOT NULL,
    discountThreshold1  NUMBER(12, 2)   DEFAULT 0.00 NOT NULL,
    discountPercent1    NUMBER(5, 4)    DEFAULT 0.0000 NOT NULL,
    discountThreshold2  NUMBER(12, 2)   DEFAULT 0.00 NOT NULL,
    discountPercent2    NUMBER(5, 4)    DEFAULT 0.0000 NOT NULL,
    CONSTRAINT PK_ShippingPricing PRIMARY KEY (shipperId, fromLoc, toLoc),
    CONSTRAINT FK_ShippingPricing_Shipper FOREIGN KEY (shipperId)
        REFERENCES Shippers(shipperId) ON DELETE CASCADE,
    CONSTRAINT CHK_Ship_MinPrice CHECK (minPackagePrice >= 0),
    CONSTRAINT CHK_Ship_PricePerLb CHECK (pricePerLb > 0),
    CONSTRAINT CHK_Ship_Disc1 CHECK (discountPercent1 >= 0.0000 AND discountPercent1 <= 1.0000),
    CONSTRAINT CHK_Ship_Disc2 CHECK (discountPercent2 >= 0.0000 AND discountPercent2 <= 1.0000),
    CONSTRAINT CHK_Ship_Thresholds CHECK (discountThreshold1 >= 0 AND discountThreshold2 >= discountThreshold1),
    CONSTRAINT CHK_Ship_DiscRate CHECK (discountPercent2 >= discountPercent1)
);

-- ============================================================================
-- 4. DEMAND
-- ============================================================================

-- Customer demand: Quantities of items demanded by end-customers.
CREATE TABLE CustomerDemand (
    customerId          VARCHAR2(30)    NOT NULL,
    itemId              VARCHAR2(30)    NOT NULL,
    demandQty           NUMBER(10)      NOT NULL,
    CONSTRAINT PK_CustomerDemand PRIMARY KEY (customerId, itemId),
    CONSTRAINT FK_CustomerDemand_Cust FOREIGN KEY (customerId)
        REFERENCES Customers(customerId) ON DELETE CASCADE,
    CONSTRAINT FK_CustomerDemand_Item FOREIGN KEY (itemId)
        REFERENCES Items(itemId) ON DELETE CASCADE,
    CONSTRAINT CHK_CustDemand_Qty CHECK (demandQty > 0)
);

-- ============================================================================
-- 5. ORDERS (RECORDED SEPARATELY)
-- ============================================================================

-- Supply Orders: Orders placed with a supplier for items.
CREATE TABLE SupplyOrders (
    orderId             VARCHAR2(30)    NOT NULL,
    supplierId          VARCHAR2(30)    NOT NULL,
    itemId              VARCHAR2(30)    NOT NULL,
    orderedQty          NUMBER(10)      NOT NULL,
    orderDate           DATE            DEFAULT SYSDATE NOT NULL,
    CONSTRAINT PK_SupplyOrders PRIMARY KEY (orderId),
    CONSTRAINT UQ_SupplyOrders_Entry UNIQUE (supplierId, itemId, orderId),
    CONSTRAINT FK_SupplyOrders_Supplier FOREIGN KEY (supplierId)
        REFERENCES Suppliers(supplierId) ON DELETE CASCADE,
    CONSTRAINT FK_SupplyOrders_Item FOREIGN KEY (itemId)
        REFERENCES Items(itemId) ON DELETE CASCADE,
    CONSTRAINT CHK_SupplyOrders_Qty CHECK (orderedQty > 0)
);

-- Manufacturing Orders: Orders placed with a manufacturer for product items.
CREATE TABLE ManufacturingOrders (
    orderId             VARCHAR2(30)    NOT NULL,
    manufId             VARCHAR2(30)    NOT NULL,
    prodItemId          VARCHAR2(30)    NOT NULL,
    orderedQty          NUMBER(10)      NOT NULL,
    orderDate           DATE            DEFAULT SYSDATE NOT NULL,
    CONSTRAINT PK_ManufacturingOrders PRIMARY KEY (orderId),
    CONSTRAINT UQ_ManufOrders_Entry UNIQUE (manufId, prodItemId, orderId),
    CONSTRAINT FK_ManufOrders_Manuf FOREIGN KEY (manufId)
        REFERENCES Manufacturers(manufId) ON DELETE CASCADE,
    CONSTRAINT FK_ManufOrders_Product FOREIGN KEY (prodItemId)
        REFERENCES ProductItems(itemId) ON DELETE CASCADE,
    CONSTRAINT CHK_ManufOrders_Qty CHECK (orderedQty > 0)
);

-- Shipping Orders: Shipments executed by shippers moving items from sender to recipient.
CREATE TABLE ShippingOrders (
    shipOrderId         VARCHAR2(30)    NOT NULL,
    shipperId           VARCHAR2(30)    NOT NULL,
    senderId            VARCHAR2(30)    NOT NULL,
    recipientId         VARCHAR2(30)    NOT NULL,
    itemId              VARCHAR2(30)    NOT NULL,
    shippedQty          NUMBER(10)      NOT NULL,
    shipDate            DATE            DEFAULT SYSDATE NOT NULL,
    CONSTRAINT PK_ShippingOrders PRIMARY KEY (shipOrderId),
    CONSTRAINT FK_ShipOrders_Shipper FOREIGN KEY (shipperId)
        REFERENCES Shippers(shipperId) ON DELETE CASCADE,
    CONSTRAINT FK_ShipOrders_Sender FOREIGN KEY (senderId)
        REFERENCES BusinessEntities(entityId) ON DELETE CASCADE,
    CONSTRAINT FK_ShipOrders_Recipient FOREIGN KEY (recipientId)
        REFERENCES BusinessEntities(entityId) ON DELETE CASCADE,
    CONSTRAINT FK_ShipOrders_Item FOREIGN KEY (itemId)
        REFERENCES Items(itemId) ON DELETE CASCADE,
    CONSTRAINT CHK_ShipOrders_Qty CHECK (shippedQty > 0),
    -- Semantic integrity constraint: Sender cannot be the recipient
    CONSTRAINT CHK_ShipOrders_NoSelfShip CHECK (senderId <> recipientId)
);

