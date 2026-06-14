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
import { Project } from "./project.js";

  
  //Adding index for faster lookups., especially if these are used frequently in WHERE clauses
  @Index(["name",'project_id'])
  @Index(["user_id", "project_id"])
  @Entity()
  @Unique(['user_id', 'project_id', 'name']) 
  export class Config {
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




    //set..
    @ManyToOne(() => Project, { //OneToOne
      nullable: false,
      onDelete: `CASCADE`,
      //eager: true  //If true then.. tt will load the child..
    })
    @JoinColumn({name:`project_id`,})
    project!: Project
    @Column({ name: 'project_id',nullable:false, type:`uuid` }) //add column explicitly here..for retrieval purpose..
    project_id!: string;





    //set..
    @Column({type:"varchar"})
    name!: string;  //eg=> onamoda, ecom
    



    //set..
    /*eg==>
    `It will store [data], Which can-be used my [utility]`
    */
    @Column({type:"jsonb", nullable:true, default:null})
    data!: Record<string, unknown> | null; //JSON;
  


  

    //set..
    @CreateDateColumn()
    created_at!: Date;
  
    @UpdateDateColumn()
    updated_at!: Date;
  }