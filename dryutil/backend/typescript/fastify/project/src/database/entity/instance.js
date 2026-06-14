var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
import { Column, CreateDateColumn, Entity, Index, JoinColumn, ManyToOne, PrimaryGeneratedColumn, Unique, UpdateDateColumn, } from "typeorm";
import { User } from "./user.js";
import { Project } from "./project.js";
import { Utility } from "./utility.js";
import { Config } from "./config.js";
//Adding index for faster lookups., especially if these are used frequently in WHERE clauses
let Instance = class Instance {
};
__decorate([
    PrimaryGeneratedColumn("uuid"),
    __metadata("design:type", String)
], Instance.prototype, "id", void 0);
__decorate([
    ManyToOne(() => User, {
        nullable: false,
        onDelete: `CASCADE`,
        //eager: true  //If true then.. tt will load the child..
    }),
    JoinColumn({ name: `user_id`, }),
    __metadata("design:type", User)
], Instance.prototype, "user", void 0);
__decorate([
    Column({ name: 'user_id', nullable: false }) //add column explicitly here..for retrieval purpose..
    ,
    __metadata("design:type", String)
], Instance.prototype, "user_id", void 0);
__decorate([
    ManyToOne(() => Project, {
        nullable: false,
        onDelete: `CASCADE`,
        //eager: true  //If true then.. tt will load the child..
    }),
    JoinColumn({ name: `project_id`, }),
    __metadata("design:type", Project)
], Instance.prototype, "project", void 0);
__decorate([
    Column({ name: 'project_id', nullable: false }) //add column explicitly here..for retrieval purpose..
    ,
    __metadata("design:type", String)
], Instance.prototype, "project_id", void 0);
__decorate([
    ManyToOne(() => Utility, {
        nullable: false,
        onDelete: `CASCADE`,
        //eager: true  //If true then.. tt will load the child..
    }),
    JoinColumn({ name: `utility_id`, }),
    __metadata("design:type", Utility)
], Instance.prototype, "utility", void 0);
__decorate([
    Column({ name: 'utility_id', nullable: false }) //add column explicitly here..for retrieval purpose..
    ,
    __metadata("design:type", String)
], Instance.prototype, "utility_id", void 0);
__decorate([
    ManyToOne(() => Config, {
        nullable: true,
        onDelete: `CASCADE`,
        //eager: true  //If true then.. tt will load the child..
    }),
    JoinColumn({ name: `config_id`, }),
    __metadata("design:type", Config)
], Instance.prototype, "config", void 0);
__decorate([
    Column({ name: 'config_id', nullable: true }) //add column explicitly here..for retrieval purpose..
    ,
    __metadata("design:type", String)
], Instance.prototype, "config_id", void 0);
__decorate([
    Column({ type: "varchar" }),
    __metadata("design:type", String)
], Instance.prototype, "name", void 0);
__decorate([
    Column({ type: "text", nullable: true }),
    __metadata("design:type", String)
], Instance.prototype, "description", void 0);
__decorate([
    Column({ type: "jsonb", nullable: true, default: null }),
    __metadata("design:type", Object)
], Instance.prototype, "data", void 0);
__decorate([
    CreateDateColumn(),
    __metadata("design:type", Date)
], Instance.prototype, "created_at", void 0);
__decorate([
    UpdateDateColumn(),
    __metadata("design:type", Date)
], Instance.prototype, "updated_at", void 0);
Instance = __decorate([
    Index(["name", 'project_id']),
    Index(["user_id", "project_id"]),
    Entity(),
    Unique(['user_id', 'project_id', 'name'])
], Instance);
export { Instance };
