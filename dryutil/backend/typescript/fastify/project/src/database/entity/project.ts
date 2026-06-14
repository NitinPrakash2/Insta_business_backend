import {
    Column,
    CreateDateColumn,
    Entity,
    Index,
    JoinColumn,
    ManyToOne,
    OneToOne,
    PrimaryGeneratedColumn,
    Unique,
    UpdateDateColumn,
    
} from "typeorm";
import { User } from "./user.js";

  
  //Adding index for faster lookups., especially if these are used frequently in WHERE clauses
  @Index(["name"])
  @Entity()
  @Unique(['name']) //@Unique(['user_id', 'name'])  eg => `https://api.example.com/{project_name=ecom}/{instance_name=login}` behind the scene it is using for-eg `utility_name=login_with_jwt_token`
  export class Project {
    @PrimaryGeneratedColumn("uuid")
    id!: string;
  

    @ManyToOne(() => User, { //OneToOne
      nullable: false,
      onDelete: `CASCADE`,
      //eager: true  //If true then.. tt will load the child..
    })
    @JoinColumn({name:`user_id`,})
    user!: User
    @Column({ name: 'user_id',nullable:false, type:`uuid` }) //add column explicitly here..for retrieval purpose..
    user_id!: string;




    @Column({type:"varchar"})
    name!: string;  //eg=> onamoda, ecom
    
  


  

    //set..
    @CreateDateColumn()
    created_at!: Date;
  
    @UpdateDateColumn()
    updated_at!: Date;
  }