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
import { Utility } from "./utility.js";
import { Config } from "./config.js";

  
  //Adding index for faster lookups., especially if these are used frequently in WHERE clauses
  @Index(["name",'project_id'])
  @Index(["user_id", "project_id"])
  @Entity()
  @Unique(['user_id', 'project_id', 'name']) 
  export class Instance {
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
    @ManyToOne(() => Utility, { //OneToOne
      nullable: false,
      onDelete: `CASCADE`,
      //eager: true  //If true then.. tt will load the child..
    })
    @JoinColumn({name:`utility_id`,})
    utility!: Utility
    @Column({ name: 'utility_id',nullable:false, type:`int` }) //add column explicitly here..for retrieval purpose..
    utility_id!: string;





    //set..
    @ManyToOne(() => Config, { //OneToOne
      nullable: true,
      onDelete: `CASCADE`,
      //eager: true  //If true then.. tt will load the child..
    })
    @JoinColumn({name:`config_id`,})
    config!: Config
    @Column({ name: 'config_id',nullable:true, type:`uuid` }) //add column explicitly here..for retrieval purpose..
    config_id!: string;




    //set..
    @Column({type:"varchar"})
    name!: string;  //eg=> onamoda, ecom
    



    //set..
    @Column({ type: "text", nullable: true })
    description?: string;






    //set..
    /*eg==>
    `It will store [data], Which can-be used by [utility]`
    */
    @Column({type:"jsonb", nullable:true, default:null})
    data!: Record<string, unknown> | null; //JSON;
  

    


  

    //set..
    @CreateDateColumn()
    created_at!: Date;
  
    @UpdateDateColumn()
    updated_at!: Date;
  }