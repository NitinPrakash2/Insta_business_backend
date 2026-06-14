import {
    Column,
    CreateDateColumn,
    Entity,
    PrimaryGeneratedColumn,
    UpdateDateColumn,
    Index,
} from "typeorm";
  
  //Adding index for faster lookups on email, client_id, etc., especially if these are used frequently in WHERE clauses
  @Index(["email"])
  //@Index(["client_id"])
  @Index(["secret_key"])
  @Entity() //{ name: "user" }
  export class User {
    @PrimaryGeneratedColumn("uuid")
    id!: string;
  
    @Column({ type: "varchar", length: 155 })
    name!: string;
  
    @Column({ type: "varchar", length: 95, unique: true})
    email!: string;
  
    @Column({ type: "varchar", length: 155, select: false })
    pwd!: string;



    //set..
    @Column({ type: "varchar", length: 155, select: false, unique: true, nullable:true })
    secret_key!: string;
    /* Currently not required.. Because we have a `project_id` OR `project_name` concept..
    @Column({ type: "varchar", length: 155, select: false, unique: true })
    client_id!: string;*/



  

    @CreateDateColumn()
    created_at!: Date;
  
    @UpdateDateColumn()
    updated_at!: Date;
  }