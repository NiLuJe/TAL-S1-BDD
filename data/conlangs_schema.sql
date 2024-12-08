PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

CREATE TABLE Phonology (
	ID INTEGER NOT NULL,
	LangID INTEGER,
	PhonemeID INTEGER,
	CONSTRAINT Phonology_PK PRIMARY KEY (ID),
	CONSTRAINT Phonology_LangInfo_FK FOREIGN KEY (LangID) REFERENCES LangInfo (LangID),
	CONSTRAINT Phonology_PhonemeBank_FK FOREIGN KEY (ID) REFERENCES PhonemeBank (PhonemeID)
);

CREATE TABLE LangInfo (
	LangID INTEGER NOT NULL,
	LangName TEXT NOT NULL,
	Creator TEXT NOT NULL,
	World TEXT,
	Spoken INTEGER NOT NULL DEFAULT (TRUE),
	Written INTEGER NOT NULL DEFAULT (FALSE),
	Usage TEXT,
	Description TEXT,
	CONSTRAINT LangInfo_PK PRIMARY KEY (LangID)
);

CREATE TABLE Prosody (
	ID INTEGER NOT NULL,
	LangID INTEGER,
	PhonemicStress INTEGER NOT NULL DEFAULT (FALSE),
	SyllableWeightStress INTEGER NOT NULL DEFAULT (TRUE),
	CONSTRAINT Prosody_PK PRIMARY KEY (ID),
	CONSTRAINT Prosody_LangInfo_FK FOREIGN KEY (LangID) REFERENCES LangInfo (LangID)
);

CREATE TABLE Lexicon (
	ID INTEGER NOT NULL,
	LangID INTEGER,
	Native_Word TEXT,
	EN_Word TEXT,
	FR_Word TEXT,
	IPA_Word TEXT,
	CONSTRAINT Lexicon_PK PRIMARY KEY (ID),
	CONSTRAINT Lexicon_LangInfo_FK FOREIGN KEY (LangID) REFERENCES LangInfo (LangID)
);

CREATE TABLE MorphoSyntax (
	ID INTEGER NOT NULL,
	LangID INTEGER,
	WordOrder TEXT,
	PluralCount INTEGER,
	CaseCount INTEGER,
	AdjectiveBeforeNoun INTEGER,
	AdjectiveAfterNoun INTEGER,
	AdjectiveAgreement INTEGER,
	CONSTRAINT MorphoSyntax_PK PRIMARY KEY (ID),
	CONSTRAINT MorphoSyntax_LangInfo_FK FOREIGN KEY (LangID) REFERENCES LangInfo (LangID)
);

CREATE TABLE PhonemeFeature (
	ID INTEGER NOT NULL,
	Name TEXT,
	CONSTRAINT PhonemeFeature_PK PRIMARY KEY (ID)
);

CREATE TABLE Inspiration (
	ID INTEGER NOT NULL,
	LangID INTEGER,
	NaturalLanguage TEXT,
	PhonologyFeature INTEGER,
	ProsodyFeature TEXT,
	MorphoSyntaxFeature TEXT,
	CONSTRAINT Inspiration_PK PRIMARY KEY (ID),
	CONSTRAINT Inspiration_LangInfo_FK FOREIGN KEY (LangID) REFERENCES LangInfo (LangID),
	CONSTRAINT Inspiration_PhonemeFeature_FK FOREIGN KEY (PhonologyFeature) REFERENCES PhonemeFeature (ID)
);

CREATE TABLE PhonemeBank (
	PhonemeID INTEGER NOT NULL,
	IPA TEXT NOT NULL,
	Type TEXT NOT NULL,
	Vowel_Height TEXT,
	Vowel_Backness TEXT,
	Vowel_Roundness TEXT,
	Consonant_Voicing INTEGER,
	Consonant_ArticulationManner TEXT,
	Consonant_ArticulationPlace TEXT,
	Modifiers TEXT,
	Feature INTEGER,
	CONSTRAINT PhonemeBank_PK PRIMARY KEY (PhonemeID),
	CONSTRAINT PhonemeBank_PhonemeFeature_FK FOREIGN KEY (Feature) REFERENCES PhonemeFeature (ID)
);

CREATE UNIQUE INDEX Phonology_ID_IDX ON Phonology (ID);

CREATE UNIQUE INDEX LangInfo_LangID_IDX ON LangInfo (LangID);

CREATE UNIQUE INDEX Prosody_ID_IDX ON Prosody (ID);

CREATE UNIQUE INDEX Lexicon_ID_IDX ON Lexicon (ID);

CREATE UNIQUE INDEX MorphoSyntax_ID_IDX ON MorphoSyntax (ID);

CREATE UNIQUE INDEX PhonemeFeature_ID_IDX ON PhonemeFeature (ID);

CREATE UNIQUE INDEX PhonemeBank_PhonemeID_IDX ON PhonemeBank (PhonemeID);

CREATE INDEX PhonemeBank_IPA_IDX ON PhonemeBank (IPA);

CREATE INDEX PhonemeBank_Type_IDX ON PhonemeBank (Type);

COMMIT;
