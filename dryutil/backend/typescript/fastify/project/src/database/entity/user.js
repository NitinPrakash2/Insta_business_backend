var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
import { Column, CreateDateColumn, Entity, PrimaryGeneratedColumn, UpdateDateColumn, Index, } from "typeorm";
//Adding index for faster lookups on email, client_id, etc., especially if these are used frequently in WHERE clauses
let User = class User {
};
__decorate([
    PrimaryGeneratedColumn("uuid"),
    __metadata("design:type", String)
], User.prototype, "id", void 0);
__decorate([
    Column({ type: "varchar", length: 155 }),
    __metadata("design:type", String)
], User.prototype, "name", void 0);
__decorate([
    Column({ type: "varchar", length: 95, unique: true }),
    __metadata("design:type", String)
], User.prototype, "email", void 0);
__decorate([
    Column({ type: "varchar", length: 155, select: false }),
    __metadata("design:type", String)
], User.prototype, "pwd", void 0);
__decorate([
    Column({ type: "varchar", length: 155, select: false, unique: true, nullable: true }),
    __metadata("design:type", String)
], User.prototype, "secret_key", void 0);
__decorate([
    CreateDateColumn(),
    __metadata("design:type", Date)
], User.prototype, "created_at", void 0);
__decorate([
    UpdateDateColumn(),
    __metadata("design:type", Date)
], User.prototype, "updated_at", void 0);
User = __decorate([
    Index(["email"])
    //@Index(["client_id"])
    ,
    Index(["secret_key"]),
    Entity() //{ name: "user" }
], User);
export { User };
