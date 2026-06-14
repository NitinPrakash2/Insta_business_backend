import {
  Column,
  Entity,
  PrimaryColumn,
} from "typeorm";

@Entity()
export class Utility {
  @PrimaryColumn({ type: "int", })
  id!: number;

  @Column({ type: "varchar", length: 155, unique: true })
  name!: string;

  @Column({ type: "text", nullable: true })
  description?: string;

}