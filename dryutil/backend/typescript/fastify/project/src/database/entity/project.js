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
//Adding index for faster lookups., especially if these are used frequently in WHERE clauses
let Project = class Project {
};
__decorate([
    PrimaryGeneratedColumn("uuid"),
    __metadata("design:type", String)
], Project.prototype, "id", void 0);
__decorate([
    ManyToOne(() => User, {
        nullable: false,
        onDelete: `CASCADE`,
        //eager: true  //If true then.. tt will load the child..
    }),
    JoinColumn({ name: `user_id`, }),
    __metadata("design:type", User)
], Project.prototype, "user", void 0);
__decorate([
    Column({ name: 'user_id', nullable: false }) //add column explicitly here..for retrieval purpose..
    ,
    __metadata("design:type", String)
], Project.prototype, "user_id", void 0);
__decorate([
    Column({ type: "varchar" }),
    __metadata("design:type", String)
], Project.prototype, "name", void 0);
__decorate([
    CreateDateColumn(),
    __metadata("design:type", Date)
], Project.prototype, "created_at", void 0);
__decorate([
    UpdateDateColumn(),
    __metadata("design:type", Date)
], Project.prototype, "updated_at", void 0);
Project = __decorate([
    Index(["name"]),
    Entity(),
    Unique(['name']) //@Unique(['user_id', 'name'])  eg => `https://api.example.com/{project_name=ecom}/{instance_name=login}` behind the scene it is using for-eg `utility_name=login_with_jwt_token`
], Project);
export { Project };
